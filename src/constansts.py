import os
from typing import Any
from src.exceptions import NotFoundToken
import requests
from dataclasses import dataclass

API_VERSION = 5.199
BASE_API_URL = "https://api.vk.com/method/"
TOKEN = os.getenv("AUTH_TOKEN")
# if not TOKEN:
#     raise NotFoundToken("Token is not found in the environment of variables")

@dataclass
class BASE_URL:
    _GET_WALLS = "wall.get?domain={}&count=100&offset={}"
    _GET_UPLOAD_SERVER = "photos.getWallUploadServer?group_id={}"
    _GET_GROUP_ID = "wall.get?domain={}&count=100&offset=1"
    _SAVE_PHOTO = "photos.saveWallPhoto?group_id={}&photo={}&server={}&hash={}"
    _PUBLISH_PROPOSED = "wall.post?owner_id=-{}&from_group=1"
    _PUBLISH_DEFERRED = "wall.post?owner_id=-{}&publish_date={}&from_group=1"

    def _formatter(self, pattern):
        return f"{BASE_API_URL}{pattern}&access_token={TOKEN}&v={API_VERSION}"


class URL(BASE_URL):
    def __init__(self, domain):
        self.domain = domain
        self._get_upload_server = None
        self._group_id = None
        self._save_photo = None
        self._upload_post = None

    def __get_group_id(self):
        url = self._formatter(self._GET_GROUP_ID.format(self.domain))
        return abs(requests.get(url=url, timeout=2).json()['response']['items'][1]['owner_id'])

    @property
    def get_walls(self):
        return self._get_walls

    @get_walls.setter
    def get_walls(self, offset):
        pattern = self._GET_WALLS.format(self.domain, offset)
        self._get_walls = self._formatter(pattern)

    @property
    def get_upload_server(self):
        if self._get_upload_server is None:
            self._get_upload_server = self._formatter(self._GET_UPLOAD_SERVER.format(self.group_id))
        return self._get_upload_server

    @property
    def group_id(self):
        if self._group_id is None:
            self._group_id = self.__get_group_id()
        return self._group_id

    @property
    def save_photo(self):
        return self._save_photo

    @save_photo.setter
    def save_photo(self, data):
        photo, server, hash_img = data
        pattern = self._SAVE_PHOTO.format(self.group_id, photo, server, hash_img)
        self._save_photo = self._formatter(pattern)

    @property
    def upload_post(self):
        if self._upload_post is None:
            self._upload_post = self._formatter(self._PUBLISH_PROPOSED.format(self.group_id))
        return self._upload_post
