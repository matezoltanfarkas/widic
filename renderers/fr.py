import bs4

from renderers.base import BaseRenderer


class Renderer(BaseRenderer):
    def __init__(self):
        super().__init__()

    def handle_dl(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        return " " + self.walk_tree(element, *args, **kwargs) + "\n"
