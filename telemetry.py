import hashlib
import os
from time import time

from requests import post
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Markdown

import config


def generate_user_id():
    # Generate a unique user ID based on the current time and a random salt
    salt = os.urandom(16)
    current_time = str(time()).encode("utf-8")
    user_id = hashlib.md5(salt + current_time).hexdigest()
    return user_id


def post_telemetry_data(user_id: str, language: str):
    telemetry_endpoint = "https://mateserver.de/telemetry"
    payload = {"userid": user_id, "lang": language}
    try:
        post(telemetry_endpoint, params=payload, timeout=5)
    except Exception:
        return None


class AcceptTelemetryButton(Button):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = "I Agree"
        self.variant = "success"
        self.id = "agree"
        self.styles.margin = (1, 2, 1, 2)


class DeclineTelemetryButton(Button):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = "I Disagree"
        self.variant = "error"
        self.id = "disagree"
        self.styles.margin = (1, 2, 1, 2)


class WidicUsageSharingText(Markdown):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = (
            "#### Hi,\n\n"
            "my name is Máté and I am the sole developer of Widic.\n\n"
            "Thank you for your trust in Widic. I hope you enjoy it and find it just as useful as I do.\n\n"
            "Now, I have no idea how many of you are out there and which languages you are using Widic for. For me personally, this is a hobby project, with which I would like to contribute to the open-source community.\n\n"
            "At the same time, I do not want to waste too much unnecessary time on something nobody is using. Unfortunately, GitHub only shows some bare cloning stats but not the entities behind it. In order to get a better picture of what should I focus on, I ask you for your permission to collect some hashed usage data.\n\n"
            "**This includes for the time being only the languages you are using Widic for.**\n\n"
            "A hypothetical revelation of this data would be something like: most users fire up Widic for language XY but then never after. This would indicate there's something wrong with the rendering of language XY.\n\n"
            "I do not care about your queries and I have no interest in you personally. If that was the case, I would aleady be running some malicious code on your machine.\n\n"
            "In order to keep your trust, I would like to be as transparent about this as possible. You can find the implementation of the telemetry stuff here: `https://github.com/matezoltanfarkas/widic/blob/main/telemetry.py`\n\n"
            "Obviously, the defaults are set to off. You can find your id in the config file at `~/.config/widic.yaml`.\n\n"
            "In case something changes in this regard, I will let you know in a similar annoying message like this one.\n\n"
        )

    def on_mount(self) -> None:
        self.update(self.text)


class WidicUsageSharingScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.border_title = "A Message from Widic's Developer"

    def on_mount(self) -> None:
        markdown_widget = self.query_one(WidicUsageSharingText)
        markdown_widget.update(markdown_widget.text)

    def compose(self) -> ComposeResult:
        agree_button = AcceptTelemetryButton()
        disagree_button = DeclineTelemetryButton()
        vertical_scroll_container = VerticalScroll(WidicUsageSharingText())
        horizontal_container = Horizontal(agree_button, disagree_button)
        horizontal_container.styles.align = ("center", "top")
        horizontal_container.styles.height = "30%"
        yield vertical_scroll_container
        yield horizontal_container

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "agree":
            self.dismiss(True)
        elif event.button.id == "disagree":
            self.dismiss(False)
