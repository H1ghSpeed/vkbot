from src.client import Client
import asyncio
from src.services import shuffle_posts


class Poster(Client):
    async def publish_one_post(self, post_id):
        self.file_manager.post_id = post_id
        text_task = asyncio.create_task(self._read_file(self.file_manager.text_post_path), name="text")
        tasks = [asyncio.create_task(self._upload_image_for_server(image_path), name=f"image_{num}")
                                    for num, image_path in enumerate(self.file_manager.images_post_path)]
        tasks.append(text_task)
        await asyncio.gather(*tasks)

        loaded_photos = [0 * (len(tasks) - 1)]
        post = {"Content-Type": "multipart/form-data"}
        for task in tasks:
            if task.get_name() == "text":
                post["message"] = task.result()
            else:
                index = int(task.get_name().split("_")[-1])
                loaded_photos[index] = task.result()
        post["attachments"] = ",".join(loaded_photos)
        await self._send_request(url=self.url.upload_post, data=post)


    async def publish_posts(self):
        tasks = []
        posts_id = shuffle_posts(self.file_manager)
        for post in posts_id:
            task = asyncio.create_task(self.publish_one_post(post))
            await task
        #     tasks.append(asyncio.create_task(self.publish_one_post(post)))
        # await asyncio.gather(*tasks)
