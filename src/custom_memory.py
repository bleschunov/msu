from dataclasses import dataclass


@dataclass
class HumanMessage:
    message: str

    def get_message(self):
        return "Human: " + self.message + "\n"


@dataclass
class AiMessage:
    message: str

    def get_message(self):
        return "AI: " + self.message + "\n"


class CustomMemory:
    def __init__(self):
        self.messages: list[AiMessage | HumanMessage] = []

    def get_memory(self):
        if len(self.messages) == 0:
            return ""
        return "Chat history:\n" + "".join([message.get_message() for message in self.messages])

    def add_message(self, message: AiMessage | HumanMessage):
        self.messages.append(message)
        return self

    def __repr__(self):
        return self.get_memory()
