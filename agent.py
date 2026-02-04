from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelMessage

from prompts import PLANNING_PROMPT
from tools import edit, execute, glob_files, read, search, write

_agent = Agent(
    model="openai:gpt-5-mini",
    tools=[
        read,
        search,
        edit,
        write,
        execute,
        glob_files,
    ],
)


class Extras(BaseModel):
    db_schema: str = Field(
        description="The database schema for the project. Do not include followup question when writing the database schema."
    )
    api_endpoints: str = Field(
        description="The API endpoints for the project. Do not include followup question when writing the API endpoints."
    )
    ui_layout: str = Field(
        description="The UI layout for the project. Do not include followup question when writing the UI layout."
    )
    design_system: str = Field(
        description="The design system for the project. Do not include followup question when writing the design system."
    )


class PlanningResponse(BaseModel):
    overview: str = Field(
        description="A brief overview of the project. Do not include followup question when writing the overview."
    )
    tech_stack: str = Field(
        description="The technology stack to be used for the project. Do not include followup question when writing the tech stack."
    )
    prerequisites: str = Field(
        description="The prerequisites for the project. Do not include followup question when writing the prerequisites."
    )
    core_features: str = Field(
        description="The core features of the project. Do not include followup question when writing the core features."
    )
    key_interactions: str = Field(
        description="The key interactions of the project. Do not include followup question when writing the key interactions."
    )
    implementation_plan: str = Field(
        description="The implementation plan for the project. Do not include followup question when writing the implementation plan."
    )
    success_criteria: str = Field(
        description="The success criteria for the project. Do not include followup question when writing the success criteria."
    )
    extras: Extras = Field(
        description="Optional information for the project. Do not include followup question when writing the additional information."
    )


class QuestionResponse(BaseModel):
    question: str = Field(
        description="A question to ask the user. Do not include the plan when writing the question."
    )


def planning_response_to_markdown(plan: PlanningResponse) -> str:
    """Convert a PlanningResponse to markdown format."""
    md = "# Project Specification\n\n"
    md += f"## Overview\n{plan.overview}\n\n"
    md += f"## Tech Stack\n{plan.tech_stack}\n\n"
    md += f"## Prerequisites\n{plan.prerequisites}\n\n"
    md += f"## Core Features\n{plan.core_features}\n\n"
    md += f"## Key Interactions\n{plan.key_interactions}\n\n"
    md += f"## Implementation Plan\n{plan.implementation_plan}\n\n"
    md += f"## Success Criteria\n{plan.success_criteria}\n\n"
    md += f"## Database Schema\n{plan.extras.db_schema}\n\n"
    md += f"## API Endpoints\n{plan.extras.api_endpoints}\n\n"
    md += f"## UI Layout\n{plan.extras.ui_layout}\n\n"
    md += f"## Design System\n{plan.extras.design_system}\n"
    return md


async def planning_step(
    user_prompt: str, message_history: list[ModelMessage], project_dir: Path
):
    if not project_dir.exists():
        project_dir.mkdir(parents=True)

    agent = Agent(
        model="google-gla:gemini-3-flash-preview",
        instructions=PLANNING_PROMPT,
        output_type=PlanningResponse | QuestionResponse,
    )

    response = await agent.run(
        user_prompt + "\nHere is the project directory: " + str(project_dir),
        message_history=message_history,
    )
    output = response.output
    print(output)

    if isinstance(output, QuestionResponse):
        return "continue", output.question, response.new_messages()
    elif isinstance(output, PlanningResponse):
        markdown_content = planning_response_to_markdown(output)
        with open(project_dir / "app_spec.md", "w") as f:
            f.write(markdown_content)
        return "done", markdown_content, response.new_messages()
    else:
        return "error", "Unexpected response type"


if __name__ == "__main__":
    import asyncio

    async def main():
        project_dir = Path("project")
        user_prompt = (
            "create a todo to build an rl environment to simulate tool calling in llms"
        )
        messages = []

        while True:
            status, *response, new_messages = await planning_step(
                user_prompt, messages, project_dir
            )
            messages.extend(new_messages)

            if status == "done":
                print("\n✓ Planning complete!")
                break
            elif status == "continue":
                question = response[0]
                print(f"\nAgent: {question}")
                user_prompt = input("You: ").strip()
            else:
                print(f"Error: {response[0] if response else 'Unknown error'}")
                break

    asyncio.run(main())
