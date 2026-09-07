import bs4


class Renderer:
    def render_list(
        self, list_tag: bs4.element.Tag, depth: int = 0, *args, **kwargs
    ) -> str:
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
        for index, li in enumerate(dd_items, start=1):
            indent = "  " * depth
            prefix = f"{index}. " if list_tag.name == "ol" else "- "
            parts = "" + self.walk_tree(li, depth + 1, *args, **kwargs)
            if parts == "":
                continue
            markdown += f"\n{indent}{prefix}{parts}\n"
        return markdown

    def render_text(self, element: bs4.element.Tag, notextformat: bool = False) -> str:
        markdown = ""
        if notextformat and element.name not in ["span", "a"]:
            return element.get_text()
        match element.name:
            # case "h1":
            # markdown += "# " + element.get_text() + "\n"
            case "h2":
                markdown += "\n# " + element.get_text() + "\n"
            case "h3":
                markdown += "\n----------------"
                markdown += "\n## " + element.get_text() + "\n"
            case "h4":
                markdown += "\n### " + element.get_text() + "\n"
            case "p":
                # markdown += "\n" + self.walk_tree(element)+"\n"
                markdown += "\n### " + element.get_text() + "\n"
            case "a":
                if "role" in element.attrs.keys() and element["role"] == "button":
                    pass
                else:
                    markdown += self.walk_tree(element, notextformat=notextformat)
            case "b":
                content = self.walk_tree(element)
                if content.strip() == "":
                    return markdown
                markdown += "**" + content
                if markdown.endswith(" "):
                    markdown = markdown[:-1]
                markdown += "**"
            case "strong":
                content = self.walk_tree(element)
                if content.strip() == "":
                    return markdown
                markdown += "**" + content
                if markdown.endswith(" "):
                    markdown = markdown[:-1]
                markdown += "**"
            case "i":
                content = self.walk_tree(element)
                if content.strip() == "":
                    return markdown
                markdown += "*" + content
                if markdown.endswith(" "):
                    markdown = markdown[:-1]
                markdown += "*"
            case "span":
                if "class" in element.attrs.keys() and "nyms" in element["class"]:
                    pass
                elif (
                    "class" in element.attrs.keys()
                    and "nyms-toggle" in element["class"]
                ):
                    pass
                else:
                    markdown += self.walk_tree(element, notextformat=notextformat)
            case "div":
                if "class" in element.attrs.keys() and "NavFrame" in element["class"]:
                    pass
                elif (
                    "class" in element.attrs.keys() and "checktrans" in element["class"]
                ):
                    pass
                elif (
                    "class" in element.attrs.keys()
                    and "disambig-see-also" in element["class"]
                ):
                    pass
                else:
                    markdown += self.walk_tree(element, notextformat=notextformat)
            # case "dl":
            # markdown += "\n`" + self.walk_tree(element, notextformat=True)+"`\n"
        return markdown

    def walk_tree(
        self, htmltree: bs4.element.Tag, depth: int = 0, notextformat: bool = False
    ) -> str:
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
                    markdown += self.render_list(
                        child, depth, notextformat=notextformat
                    )
                    continue
                elif child.name in (
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "p",
                    "a",
                    "b",
                    "strong",
                    "i",
                    "span",
                    "div",
                ):
                    markdown += self.render_text(child, notextformat=notextformat)
                    continue
                markdown += self.walk_tree(child, notextformat=notextformat)
        return markdown
