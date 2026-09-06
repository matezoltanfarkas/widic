from argparse import ArgumentParser

import bs4
from requests import get
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Header, Log, Markdown


class WidicSourceRenderer(Markdown):
    def on_mount(self) -> None:
        pass
        # self.styles.height = "50%"

# class WidicSourceContainer(Log):
#     def on_mount(self) -> None:
#         pass
#         # self.styles.height = "50%"


class WidicHeader(Header):
    def __init__(self) -> None:
        super().__init__()
        self.widic_page_title = "Widic"

    def on_mount(self) -> None:
        self.screen.title = self.widic_page_title

    def format_title(self) -> str:
        return self.screen.title+self.screen_sub_title

class Widic(App):
    def __init__(self, args) -> None:
        super().__init__()
        self.args = args
    
    def on_mount(self) -> None:
        self.screen.terminal_title = "Widic"
        content = open(f"{self.args.language}_wiki_hello_orig.html", "r").read()
        # content = get("https://en.wiktionary.org/w/rest.php/v1/page/hello/html",headers={"User-Agent": "Widic"}).text
        # content = get("https://de.wiktionary.org/w/rest.php/v1/page/Schriftsteller/html",headers={"User-Agent": "Widic"}).text
        content = get(f"https://{self.args.language}.wiktionary.org/w/rest.php/v1/page/{self.args.word}/html",headers={"User-Agent": "Widic"}).text
        soup = bs4.BeautifulSoup(content)

        widic_header = self.query_one(WidicHeader)
        widic_header.screen.title = soup.head.title.string

        # widic_scrollable_container = self.query_one(VerticalScroll)
        # widic_scrollable_container.styles.height = "50%"
        # widic_scrollable_container.VerticalScroll = True

        widic_source_renderer = self.query_one(WidicSourceRenderer)
        markdown = self.renderhtml(soup, language=self.args.language)
        print(markdown, file=open("test.md", "w"))
        widic_source_renderer.update(markdown)
        
        # widic_source_container = self.query_one(WidicSourceContainer)
        # widic_source_container.write(soup.prettify())

    def compose(self) -> ComposeResult:
        yield WidicHeader()
        yield VerticalScroll(WidicSourceRenderer())
        # yield WidicSourceContainer()

    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()
    
    def renderhtml(self, htmlsoup: bs4.BeautifulSoup, language="en") -> str:
        markdown = ""
        # ignore scripts, styles, and tables...
        for i in htmlsoup.find_all(["script", "style", "table", "figure"]):
            i.decompose()
        # filter classes
        for i in htmlsoup.find_all(class_=["mw-editsection", "reference", "reflist", "noprint", "metadata", "was-wotd", "interproject-box", "nyms-toggle"]):
            i.decompose()
        # check language and import the appropriate renderer
        match language:
            case "en":
                from renderers.en import Renderer
            case "de":
                from renderers.de import Renderer
            case _:
                self.log(f"Unsupported language: {language}, defaulting to English")
                from renderers.en import Renderer
        # let's go!!
        markdown += Renderer().walk_tree(htmlsoup.body)
        return markdown


if __name__ == "__main__":
    parser = ArgumentParser(description="Widic - A terminal-based Wiktionary reader.")
    # language parameter with -l key
    parser.add_argument("--language", "-l", type=str, default="en", help="Language of the Wiktionary page (default: en)")
    # word parameter is the last parameter, and is required
    parser.add_argument("word", type=str, help="Word to look up in Wiktionary")
    args = parser.parse_args()
    app = Widic(args)
    app.run()
