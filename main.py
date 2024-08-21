from src.parser import Parser
from src.poster import Poster
import asyncio
import os


async def main_parser():
    client = Parser(domain="", offset=0)
    try:
        await client.get_one_hungred_posts()
    finally:
        await client.session.close()


async def main_poster():
    client = Poster(domain="")
    try:
        await client.publish_posts()
    finally:
        await client.session.close()

if __name__ == "__main__":
    asyncio.run(main_poster())
