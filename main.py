from src.parser import Parser
import asyncio
import os


async def main():
    client = Parser(domain="sekrety_zdorovya", offset=0)
    await client.get_one_hungred_posts()

if __name__ == "__main__":
    asyncio.run(main())