import asyncio
import aiohttp
import aiofiles
from constansts import URL

class Client:
    """Base client."""

    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.url_walls = URL(domain=None, offset=None)

    async def __send_request(self, url, data = None):
        """
        Send request to server.
        Args:
            url: url to request.
            data: if post request.
        Returns:
            JSON object response.
        """
        if data:
            async with self.session.post(url=url, data=data) as response:
                return await response.json()
        else:
            async with self.session.get(url=url) as response:
                return await response.json()

    async def __get_image(self, image_url):
        """
        Get image from server.
        Args:
            image_url: url to image on server.
        Returns:
            asyincio task with upload image.
        """
        return await asyncio.create_task(self.__send_request(image_url))

    async def __save_text_in_file(self, text: str, post_id: str) -> None:
        """
        Save text from post in file.
        Args:
            text: text from post.
            post_id: id from post.
        Returns:
            Saved text file.
        """
        async with aiofiles.open(post_id, "w") as file:
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
            if text_post.find(stop_key):
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
            raise Exception("Max count = 100")
        posts = await asyncio.create_task(self.__send_request(self.url_walls))['response'].get('items')
        filtered_posts = (post for post in posts if self.__filtered_post(post))
        tasks = []
        for num, post in enumerate(filtered_posts):
            if num > count:
                break
            imgs = [img for img in post["attachments"]['photo']['sizes'][-1]['url']]
            tasks.append(*[asyncio.create_task(self.__get_image(img)) for img in imgs])
            tasks.append(asyncio.create_task(self.__save_text_in_file(post["text"], post["id"])))
        await asyncio.gather(*tasks)
        # log.info(f"{num} постов собрано")
