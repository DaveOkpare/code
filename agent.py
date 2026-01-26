import asyncio

from pydantic_ai import Agent

from tools import edit_file, execute, grep_search, read_file, write

_agent = Agent(
    model="openai:gpt-5-mini",
    tools=[
        read_file,
        grep_search,
        edit_file,
        write,
        execute,
    ],
)


if __name__ == "__main__":

    async def main():
        result = await _agent.run("what are the files in my current directory?")
        return result.output

    result = asyncio.run(main())
    print(result)
