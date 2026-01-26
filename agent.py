import asyncio

from pydantic_ai import Agent

from tools import edit, execute, read, search, write

_agent = Agent(
    model="openai:gpt-5-mini",
    tools=[
        read,
        search,
        edit,
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
