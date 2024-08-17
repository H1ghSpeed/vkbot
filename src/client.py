import asyncio
import aiohttp
import os
import aiofiles
from src.constansts import URL
from src.raises import ExcessQuantityPosts
from services import FileManager, shuffle_posts

class Client:
    """Base client."""

    def __init__(self, domain):
        self.session = aiohttp.ClientSession()
        self.url_walls = URL(domain=domain, offset=0).get_walls
        self.file_manager = FileManager(domain=domain)

    async def _send_request(self, url: str, data: dict = None, image_load = False) -> aiohttp.ClientResponse:
        """
        Send request to server.
        Args:
            url: url to request.
            data: if post request.
        Returns:
            JSON object response.
        """
        if image_load:
            response = await self.session.get(url=url)
            return await response.read()
        elif data is None:
            response = await self.session.get(url=url)
            return await response.json()
        else:
            response = await self.session.post(url=url, data=data)
            return await response.json()

    async def __get_image(self, image_url:  str, filename: str, post_id: int) -> None:
        """
        Get image from server.
        Args:
            image_url: url to image on server.
            filename: filename image.
        Returns:
            asyincio task with upload image.
        """
        image = await self._send_request(image_url, image_load=True)
        async with aiofiles.open(self.file_manager.image_path / str(post_id) / filename, "wb") as file:
            await file.write(image)

    async def __save_text_in_file(self, text: str, post_id: int) -> None:
        """
        Save text from post in file.
        Args:
            text: text from post.
        Returns:
            Saved text file.
        """
        async with aiofiles.open(self.file_manager.text_path / str(post_id) / "post.txt", "w", encoding="utf-8") as file:
            await file.write(text)

    def __filtered_post(self, post: dict) -> bool:
        """
        Filtering posts for spam.
        Args:
            post: dict post in response.
        Returns:
            bool: if post not is not spam.
        """
        text_post = post.get("text")
        if not text_post:
            return False

        for stop_key in ("источник", "https", "http", "vk", "комментариях", "реклама"):
            if text_post.find(stop_key) != -1:
                return False

        for item in post.get("attachments"):
            if item.get("type") in "photo":
                return True
        return False

    async def get_one_hungred_posts(self, count: int = 100):
        """
        Get one hundred posts.
        Args:
            count: number of posts to collect.
        """
        #text, image
        if count > 100:
            raise ExcessQuantityPosts("Max count = 100")
        posts = asyncio.create_task(self._send_request(self.url_walls))
        await posts
        posts = posts.result()['response'].get('items')
        filtered_posts = (post for post in posts if self.__filtered_post(post))
        tasks = []
        for num, post in enumerate(filtered_posts):
            if num > count:
                break
            self.file_manager.post_id = post["id"]
            imgs = [img['photo']['sizes'][-1]['url'] for img in post["attachments"]]
            tasks.append(*[asyncio.create_task(self.__get_image(img, f"{post['id']}_{num}.jpg", post_id=post["id"]))
                           for num, img in enumerate(imgs)])
            tasks.append(asyncio.create_task(self.__save_text_in_file(post["text"], post_id=post["id"])))
        await asyncio.gather(*tasks)
        self.session.close()

    async def __read_file(self, post_id: str):
        async with aiofiles.open(self.file_manager.text_path / post_id / "post.txt", "r", encoding="utf-8") as file:
            return await file.read()

    async def __read_image(self, image_path: str):
        async with aiofiles.open(image_path, "rb") as file:
            return await file.read()
    
    async def __upload_image_for_server(self, image_path: str):
        await self.__read_image(image_path)

    async def publish_posts(self):
        tasks = []
        posts = shuffle_posts(self.file_manager)
        for post in posts:
            tasks.append(asyncio.create_task(self.__read_file(post.name), name="text"))
