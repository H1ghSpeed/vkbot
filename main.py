from src.client import Client
import asyncio
import os


async def main():
    client = Client(domain="sekrety_zdorovya")
    await client.get_one_hungred_posts()

if __name__ == "__main__":
    asyncio.run(main())