import uuid
from abc import abstractmethod
from dataclasses import dataclass

import pandas as pd
from streamlit_chat import message

from const import USER_AVATAR_URL, BOT_AVATAR_URL


@dataclass
class MessageContent:
    content: str | pd.DataFrame

    @abstractmethod
    def get(self) -> str:
        pass


class SimpleText(MessageContent):
    def get(self) -> str:
        return self.content


class Table(MessageContent):
    def get(self) -> str:
        if self.content is not None and any(self.content):
            return self.content.to_markdown(index=False, floatfmt=".3f")
        return ""


class SqlCode(MessageContent):
    def get(self) -> str:
        if self.content:
            return f"~~~sql\n{self.content}\n~~~"
        return ""


@dataclass
class Message:
    content_items: list[MessageContent]
    is_user: bool
    key: str = None

    def __post_init__(self):
        self.key = uuid.uuid4().hex

    def display(self):
        message_content = "\n".join(
            message_content.get() or "" for message_content in self.content_items
        )
        avatar_url = USER_AVATAR_URL if self.is_user else BOT_AVATAR_URL
        message(message_content, self.is_user, key=self.key, logo=avatar_url)
