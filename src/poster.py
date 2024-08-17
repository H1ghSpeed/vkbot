from client import Client
import asyncio
from services import shuffle_posts


class Poster(Client):
    async def publish_posts(self):
        tasks = []
        posts = shuffle_posts(self.file_manager)
        for post in posts:
            tasks.append(asyncio.create_task(self.__read_file(post.name), name="text"))
            [asyncio.create_task(self.__upload_image_for_server(image_path) for image_path in post.)]
            tasks.append()
            