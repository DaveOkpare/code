import asyncio

from pydantic_ai import Agent
from pydantic_ai_todo import TodoStorage, create_todo_toolset

from tools import edit, execute, glob_files, read, search, write

storage = TodoStorage()

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
    toolsets=[create_todo_toolset(storage=storage)],
)


if __name__ == "__main__":

    async def main():
        result = await _agent.run(
            "create a todo to build an rl environment to simulate tool calling in llms"
        )
        return result.output

    result = asyncio.run(main())
    print(result)
    print(storage.todos)
