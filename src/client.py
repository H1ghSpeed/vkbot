import asyncio
import aiohttp
import os
import time
import aiofiles
import requests
from src.constansts import URL
from src.exceptions import ExcessQuantityPosts
from src.services import FileManager, shuffle_posts
from pathlib import Path


class Client:
    """Base client."""

    def __init__(self, domain):
        self.session = aiohttp.ClientSession()
        self.url = URL(domain=domain)
        self.file_manager = FileManager(domain=domain)
        self.server = None

    async def _send_request(self, url: str, data: dict = None, image_load = False) -> aiohttp.ClientResponse:
        """
        Send request to server.
        Args:
            url: url to request.
            data: if post request.
        Returns:
            JSON object response.
        """
        if data is None:
            response = await self.session.get(url=url)
            return await response.json()
        else:
            if image_load:
                return requests.post(url=url, files=data).json()
            response = await self.session.post(url=url, data=data)
            return await response.json()

    async def _get_image(self, image_url:  str, filename: str, post_id: int) -> None:
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

    async def _save_text_in_file(self, text: str, post_id: int) -> None:
        """
        Save text from post in file.
        Args:
            text: text from post.
        Returns:
            Saved text file.
        """
        async with aiofiles.open(self.file_manager.text_path / str(post_id) / "post.txt", "w", encoding="utf-8") as file:
            await file.write(text)

    async def _read_file(self, path_to_file: Path):
        async with aiofiles.open(path_to_file / "post.txt", "r", encoding="utf-8") as file:
            return await file.read()

    async def __read_image(self, image_path: Path | str):
        async with aiofiles.open(image_path, "rb") as file:
            return await file.read()

    async def _upload_image_for_server(self, image_path: Path | str):
        server = await self._send_request(self.url.get_upload_server)
        server_url = server.get("response").get("upload_url")
        if not server_url:
            return None
        with open(image_path, "rb") as image:
            uploaded_image = await self._send_request(url=server_url, data={"photo": image}, image_load=True)
        image, server, hash_img = uploaded_image.get("photo"), uploaded_image.get("server"), uploaded_image.get("hash")
        self.url.save_photo = image, server, hash_img
        server_load = await self._send_request(self.url.save_photo)
        if "error" in server_load:
            time.sleep(1.5)
            return None
        load_photo = server_load.get("response")[0]
        owner_id, photo_id = load_photo.get("owner_id"), load_photo.get("id")
        return f"photo{owner_id}_{photo_id}"
