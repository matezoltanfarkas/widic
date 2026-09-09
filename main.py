from argparse import ArgumentParser

import sys
import re
import bs4
import requests
from requests import get
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Markdown, SelectionList
from textual.widgets.selection_list import Selection


class WidicSourceRenderer(Markdown):
    def on_mount(self) -> None:
        pass


class WidicHeader(Header):
    def __init__(self) -> None:
        super().__init__()
        self.widic_page_title = "Widic"

    def on_mount(self) -> None:
        self.screen.title = self.widic_page_title

    def format_title(self) -> str:
        return self.screen.title + self.screen_sub_title


class WidicPageChooserSelectionList(SelectionList):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.border_title = "Search Results"

    def on_mount(self) -> None:
        self.border_title = "Search Results"
        self.styles.width = "80%"
        self.styles.height = "80%"
        self.styles.align = ("center", "middle")

    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        selected_index = self.selected[0]
        selected_title = self.parent.search_results[selected_index]
        response = get(
            f"https://{self.app.args.language}.wiktionary.org/w/rest.php/v1/page/{selected_title}/html",
            headers={"User-Agent": self.app.useragent},
        )
        if response.status_code == 200:
            self.app.render_and_load_md(response, language=self.app.args.language, text_query=selected_title)


class WidicPageChooser(Screen):
    def __init__(self, search_results: list[str], text_query: str) -> None:
        super().__init__()
        self.search_results = search_results
        self.text_query = text_query

    def on_mount(self) -> None:
        # self.screen.title = f"Search Results for Article '{self.query}':"
        select = self.query_one(WidicPageChooserSelectionList)
        select.border_title = f"Search Results for Article '{self.text_query}':"
        self.styles.align = ("center", "middle")

    def compose(self) -> ComposeResult:
        selection_list = [Selection(title, i) for i, title in zip(range(len(self.search_results)), self.search_results)]
        yield WidicPageChooserSelectionList(*selection_list)


class Widic(App):
    def __init__(self, args) -> None:
        super().__init__()
        self.args = args
        self.widic_page_chooser_screen = None
        self.useragent = f"Widic/v0.1 (https://github.com/matezoltanfarkas/widic) Python-urllib/{sys.version_info[0]}.{sys.version_info[1]}"
        # content = open(f"{self.args.language}_wiki_hello_orig.html", "r").read()
        # content = get("https://en.wiktionary.org/w/rest.php/v1/page/hello/html",headers={"User-Agent": "Widic"}).text
        # content = get("https://de.wiktionary.org/w/rest.php/v1/page/Schriftsteller/html",headers={"User-Agent": "Widic"}).text
        try:
            wiktionary_site = f"https://{self.args.language}.wiktionary.org/w/rest.php/v1/page/{self.args.word}/html"
            self.response = get(
                wiktionary_site,
                headers={"User-Agent": self.useragent},
            )
        except Exception:
            self.app.exit(
                message=f"Can't fetch URL: {wiktionary_site}\n",
                return_code=-1,
            )
            return
        if self.response.status_code == 404:
            self.response_search = get(
                f"https://{self.args.language}.wiktionary.org/w/rest.php/v1/search/title?q={self.args.word}",
                headers={"User-Agent": "Widic"},
            )
            if len(self.response_search.json()["pages"]) == 0:
                self.app.exit(
                    return_code=-1,
                    message=f"No search results found for '{self.args.word}' in language '{self.args.language}'.",
                )
                return
        elif self.response.status_code != 200:
            self.app.exit(
                message=f"Wiktionary server returned an error at {wiktionary_site}\nError code: {self.response.status_code}",
                return_code=-1,
            )

    def on_mount(self) -> None:
        self.screen.terminal_title = "Widic"

        if self.response.status_code == 200:
            self.render_and_load_md(self.response, language=self.args.language, text_query=self.args.word)
        elif self.response.status_code == 404:
            titles = list(title["title"] for title in self.response_search.json()["pages"])
            self.widic_page_chooser_screen = WidicPageChooser(search_results=titles, text_query=self.args.word)
            self.push_screen(self.widic_page_chooser_screen)

    def compose(self) -> ComposeResult:
        yield WidicHeader()
        yield VerticalScroll(WidicSourceRenderer())

    def on_key(self, event) -> None:
        if event.key == "q":
            self.exit()

    def render_and_load_md(self, response: requests.Response, language="en", text_query="") -> None:
        widic_header = self.query_one(WidicHeader)
        widic_header.screen.title = text_query

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        widic_source_renderer = self.query_one(WidicSourceRenderer)
        markdown = self.renderhtml(soup, language=self.args.language)
        # print(markdown, file=open("test.md", "w"))
        widic_source_renderer.update(markdown)
        if self.widic_page_chooser_screen is not None:
            self.pop_screen()

    def renderhtml(self, htmlsoup: bs4.BeautifulSoup, language="en") -> str:
        markdown = ""
        # ignore scripts, styles, and tables...
        for i in htmlsoup.find_all(["script", "style", "table", "figure"]):
            i.decompose()
        # filter classes
        for i in htmlsoup.find_all(
            class_=[
                re.compile(x + "[^a-zA-Z0-9_\\-]")
                for x in [
                    "mw-editsection",
                    "mw-collapsible",  # a kind of collapsible table (Spanish: Translations)
                    "reference",
                    "reflist",
                    "noprint",
                    "metadata",
                    "was-wotd",  # was word of the day stuff
                    "interproject-box",
                    "nyms-toggle",
                ]
            ]
        ):
            i.decompose()
        # check language and import the appropriate renderer
        match language:
            case "en":
                from renderers.en import Renderer
            case "de":
                from renderers.de import Renderer
            case "fr":
                from renderers.fr import Renderer
            case "es":
                from renderers.es import Renderer
            case _:
                self.log(f"Unsupported language: {language}, defaulting to English")
                from renderers.en import Renderer
        # let's go!!
        markdown += Renderer().walk_tree(htmlsoup.body)
        return markdown


if __name__ == "__main__":
    parser = ArgumentParser(description="Widic - A terminal-based Wiktionary reader.")
    # language parameter with -l key
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="en",
        help="Language of the Wiktionary page (default: en)",
    )
    # word parameter is the last parameter, and is required
    parser.add_argument("word", type=str, help="Word to look up in Wiktionary")
    args = parser.parse_args()
    app = Widic(args)
    app.run()
