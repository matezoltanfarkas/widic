import bs4

from renderers.base import BaseRenderer


class Renderer(BaseRenderer):
    def __init__(self):
        super().__init__()

    def handle_h2(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        markdown += "\n# " + element.get_text() + "\n"
        return markdown

    def handle_h3(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        markdown += "\n----------------"
        markdown += "\n## " + element.get_text() + "\n"
        return markdown

    def handle_h4(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        markdown += "\n### " + element.get_text() + "\n"
        return markdown

    def handle_p(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        return self.handle_h4(element, *args, **kwargs)

    def handle_dl(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        pass

    def handle_list(self, list_tag: bs4.element.Tag, depth: int = 0, *args, **kwargs) -> str:
        markdown = ""
        li_items = list_tag.find_all("li", recursive=False)
        dd_items = list_tag.find_all("dd", recursive=False)

        for index, li in enumerate(li_items, start=1):
            indent = "  " * depth
            prefix = f"{index}. " if list_tag.name == "ol" else "- "
            parts = "" + self.walk_tree(li, depth + 1, *args, **kwargs)
            if parts == "":
                continue
            markdown += f"\n{indent}{prefix}{parts}\n"
        depth += 1
        for index, dd in enumerate(dd_items, start=1):
            indent = "  " * depth
            prefix = f"{index}. " if list_tag.name == "ol" else "- "
            parts = "" + self.walk_tree(dd, depth + 1, *args, **kwargs)
            if parts == "":
                continue
            markdown += f"\n{indent}{prefix}{parts}\n"
        return markdown

    def walk_tree(self, htmltree: bs4.element.Tag, depth: int = 0, notextformat: bool = False) -> str:
        markdown = ""
        for child in htmltree.children:
            if child == "\n":
                continue
            if child == " " and markdown.endswith(" "):
                continue
            if isinstance(child, bs4.element.NavigableString):
                markdown += child.get_text()
            if isinstance(child, bs4.element.Tag):
                if child.name in ("ul", "ol", "dl"):
                    markdown += self.handle_list(child, depth, notextformat=notextformat)
                    continue
                elif child.name in self.text_handlers.keys():
                    markdown += self.handle_text(child, notextformat=notextformat)
                    continue
                markdown += self.walk_tree(child, notextformat=notextformat)
        return markdown
