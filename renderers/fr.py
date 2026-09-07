import bs4

from renderers.base import BaseRenderer


class Renderer(BaseRenderer):
    def __init__(self):
        super().__init__()

    def handle_h1(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        return "\n# " + element.get_text() + "\n"

    def handle_h2(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n----------------"
        markdown += "\n# " + element.get_text() + "\n"
        return markdown

    def handle_h3(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n## " + element.get_text() + "\n"
        return markdown

    def handle_h4(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n### " + element.get_text() + "\n"
        return markdown

    def handle_dl(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        return " " + self.walk_tree(element, *args, **kwargs) + "\n"
