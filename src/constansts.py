import os
from typing import Any
from raises import NotFoundToken

API_VERSION = 5.131
TOKEN = os.getenv("auth_token")

if not TOKEN:
    raise NotFoundToken("Token is not found in the environment of variables")

class _BASE_URL:
    __GET_WALLS = "https://api.vk.com/method/wall.get?domain={}&count=100&offset={}&access_token={}&v={}"

    def __call__(self, *args, **kwargs):
        return str(self).format(*args, **kwargs)


class URL(_BASE_URL):
    def __init__(self, domain, offset):
        self.domain = domain
        self.offset = offset

    @property
    def get_walls(self):
        return self.__GET_WALLS.format(self.domain, self.offset, TOKEN, API_VERSION)

