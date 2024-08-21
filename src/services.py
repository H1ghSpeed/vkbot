from pathlib import Path
import random
import os


class FileManager:
    """TODO: write docs"""

    def __init__(self, domain) -> None:
        self.parent_path = Path("data")
        self.domain_path = self.parent_path / "sekrety_zdorovya"

    @property
    def post_id(self):
        return self._post_id

    @post_id.setter
    def post_id(self, post_id):
        post_id = str(post_id)
        if not (self.image_path / post_id).exists() and (self.text_path / post_id).exists():
            os.makedirs(self.domain_path / "images" / post_id, exist_ok=True)
            os.makedirs(self.domain_path / "text" / post_id, exist_ok=True)
        self._post_id = post_id

    @property
    def image_path(self):
        return self.domain_path / "images"

    @property
    def images_post_path(self):
        return (self.image_path / self.post_id).glob("*")

    @property
    def text_path(self):
        return self.domain_path / "text"

    @property
    def text_post_path(self):
        return self.text_path / self.post_id


def shuffle_posts(file_manager: FileManager) -> list:
    posts_id = os.listdir(file_manager.image_path)
    random.shuffle(posts_id)
    return posts_id
