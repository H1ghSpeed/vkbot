from pathlib import Path
import random
import os


class FileManager:
    """TODO: write docs"""

    def __init__(self, domain) -> None:
        self.parent_path = Path("data")
        self.domain_path = self.parent_path / domain

    @property
    def post_id(self):
        return self._post_id

    @post_id.setter
    def post_id(self, post_id):
        post_id = str(post_id)
        if not (self.domain_path / post_id).exists():
            os.makedirs(self.domain_path / "images" / post_id, exist_ok=True)
            os.makedirs(self.domain_path / "text" / post_id, exist_ok=True)
        self._post_id = post_id
        self.image_path = "images"
        self.text_path = "text"

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, img_path):
        self._image_path = self.domain_path/ img_path

    @property
    def text_path(self):
        return self._text_path

    @text_path.setter
    def text_path(self, text_path):
        self._text_path = self.domain_path/ text_path


def shuffle_posts(file_manager: FileManager) -> list:
    posts = os.listdir(file_manager.image_path)
    random.shuffle(posts)
    return (Path(file_manager.image_path / post) for post in posts)
