import uuid
from abc import abstractmethod

import pandas as pd
from dataclasses import dataclass

import streamlit as st
from streamlit_chat import message

from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

executor = SQLDatabaseChainExecutor(db_chain, custom_memory, debug=False)
messages_container = st.container()


class Displayable:
    @abstractmethod
    def display(self):
        pass


@dataclass
class Message(Displayable):
    text: str
    is_user: bool

    def display(self):
        message(self.text, self.is_user, key=uuid.uuid4().hex)


@dataclass
class Table(Displayable):
    df: pd.DataFrame

    def display(self):
        st.table(self.df)


def print_messages():
    for msg in st.session_state.msg_list:
        msg.display()


def reset():
    executor.reset()

    reset_message = Message("Контекст сброшен", False)
    st.session_state.msg_list.append(reset_message)

    with messages_container:
        message(reset_message.text, reset_message.is_user, key=uuid.uuid4().hex)


if "msg_list" not in st.session_state:
    st.session_state.msg_list = []

if len(st.session_state.msg_list) == 0:
    st.session_state["msg_list"].append(Message('Привет! Какой у вас запрос?', False))

with messages_container:
    print_messages()

query = st.text_input('Ваш запрос', '')

if query:
    query_message = Message(query, True)
    st.session_state.msg_list.append(query_message)

    with messages_container:
        message(query_message.text, query_message.is_user, key=uuid.uuid4().hex)

    st.session_state["input_text"] = ""

    answer, df = executor.run(query).get_all()

    answer_message = Message(answer, False)
    st.session_state.msg_list.append(answer_message)

    table = Table(df)
    st.session_state.msg_list.append(table)

    with messages_container:
        message(answer_message.text, answer_message.is_user, key=uuid.uuid4().hex)
        st.table(df)

st.button("Сбросить контекст", on_click=reset)

st.write("История сообщений: " + str(executor.get_chat_history_size()) + " токенов из ~16K")
