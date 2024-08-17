from src.client import Client
import asyncio
from src.exceptions import ExcessQuantityPosts


class Parser(Client):
    def __init__(self, domain, offset):
        super().__init__(domain)
        self.url.get_walls = offset

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
        posts = asyncio.create_task(self._send_request(self.url.get_walls))
        await posts
        posts = posts.result().get("response").get("items")
        filtered_posts = (post for post in posts if self.__filtered_post(post))
        tasks = []
        for num, post in enumerate(filtered_posts):
            if num > count:
                break
            self.file_manager.post_id = post["id"]
            imgs = [img['photo']['sizes'][-1]['url'] for img in post["attachments"]]
            tasks.append(*[asyncio.create_task(self._get_image(img, f"{post['id']}_{num}.jpg", post_id=post["id"]))
                            for num, img in enumerate(imgs)])
            tasks.append(asyncio.create_task(self._save_text_in_file(post["text"], post_id=post["id"])))
        await asyncio.gather(*tasks)
        await self.session.close()
