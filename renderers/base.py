import bs4


class BaseRenderer:
    def __init__(self):
        self.text_handlers = {
            # "h1": self.handle_h1,
            "h2": self.handle_h2,
            "h3": self.handle_h3,
            "h4": self.handle_h4,
            "p": self.handle_p,
            "a": self.handle_a,
            "b": self.handle_b,
            "strong": self.handle_strong,
            "i": self.handle_i,
            "span": self.handle_span,
            "div": self.handle_div,
            "dl": self.handle_dl,
        }

    # def handle_h1(self, element: bs4.element.Tag, *args, **kwargs) -> str:
    #     # Fun fact: <h1> seems to be reserved for the title of the article.
    #     # So maybe we should omit this one alltogether and care only for <h2+>
    #     markdown = "\n----------------"
    #     markdown += "\n# " + element.get_text() + "\n"
    #     return markdown
    #
    def handle_h2(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n\n----------------"
        markdown += "\n# " + element.get_text() + "\n"
        return markdown

    def handle_h3(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n## " + element.get_text() + "\n"
        return markdown

    def handle_h4(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n### " + element.get_text() + "\n"
        return markdown

    def handle_p(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = "\n" + self.walk_tree(element) + "\n"
        return markdown

    def handle_a(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        if "role" in element.attrs.keys() and element["role"] == "button":
            pass
        else:
            markdown += self.walk_tree(element, *args, **kwargs)
        return markdown

    def handle_b(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        content = self.walk_tree(element, *args, **kwargs)
        if content.strip() == "":
            return markdown
        markdown += "**" + content
        if markdown.endswith(" "):
            markdown = markdown[:-1]
        markdown += "**"
        return markdown

    def handle_strong(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        return self.handle_b(element, *args, **kwargs)

    def handle_i(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        content = self.walk_tree(element, *args, **kwargs)
        if content.strip() == "":
            return markdown
        if content.endswith(" "):
            content = content[:-1]
        if content.startswith(" "):
            content = content[1:]
        markdown += "*" + content
        markdown += "*"
        return markdown

    def handle_span(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        if "class" in element.attrs.keys() and "nyms" in element["class"]:
            pass
        elif "class" in element.attrs.keys() and "nyms-toggle" in element["class"]:
            pass
        else:
            markdown += self.walk_tree(element, *args, **kwargs)
        return markdown

    def handle_div(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        if "class" in element.attrs.keys() and "NavFrame" in element["class"]:
            pass
        elif "class" in element.attrs.keys() and "checktrans" in element["class"]:
            pass
        elif "class" in element.attrs.keys() and "disambig-see-also" in element["class"]:
            pass
        else:
            markdown += self.walk_tree(element, *args, **kwargs)
        return markdown

    def handle_dl(self, element: bs4.element.Tag, *args, **kwargs) -> str:
        markdown = ""
        content = self.walk_tree(element, notextformat=True)
        if content.strip() == "":
            return markdown
        markdown += " `" + content + "`\n"
        return markdown

    def handle_list(self, list_tag: bs4.element.Tag, depth: int = 0, *args, **kwargs) -> str:
        markdown = ""
        li_items = list_tag.find_all("li", recursive=False)

        for index, li in enumerate(li_items, start=1):
            indent = "    " * depth
            prefix = f"{index}. " if list_tag.name == "ol" else "- "
            parts = "" + self.walk_tree(li, depth + 1, *args, **kwargs)
            if parts == "":
                continue
            markdown += f"\n{indent}{prefix}{parts}"
        return markdown

    def handle_text(self, element: bs4.element.Tag, notextformat: bool = False) -> str:
        # English Wiktionary examples are in <dl> tags, which are turned into inline code.
        # notextformat stops bold and italic formatting which would be displayed verbatim in the examples.
        # ...unless we are in a <span> or <a> tag, which is then turned into plain text, as always
        if notextformat and element.name not in ["span", "a"]:
            return element.get_text()
        if element.name in self.text_handlers.keys():
            return self.text_handlers[element.name](element, notextformat=notextformat)
        else:
            # This should not happen, as handle_text is only called for tags that are in text_handlers.
            # But better be safe than sorry.
            # Who knows what the future holds.
            raise NotImplementedError(f"Handler for {element.name} not implemented.")

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
                if child.name in ("ul", "ol"):
                    markdown += self.handle_list(child, depth, notextformat=notextformat)
                    continue
                elif child.name in self.text_handlers.keys():
                    markdown += self.handle_text(child, notextformat=notextformat)
                    continue
                markdown += self.walk_tree(child, notextformat=notextformat)
        return markdown
