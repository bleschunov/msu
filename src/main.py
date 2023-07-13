import uuid
from abc import abstractmethod

import pandas as pd
from dataclasses import dataclass

import streamlit as st
from streamlit_chat import message


from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

SESS_STATE = st.session_state
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


def reprint_messages_from_msg_list():
    for n, msg in enumerate(st.session_state.msg_list):
        msg.display()


def initialize():
    if not SESS_STATE:
        # slow imports made here
        from chain import db_chain

        SESS_STATE.sql_chain_executor = SQLDatabaseChainExecutor(
            db_chain, custom_memory, debug=False
        )

        st.session_state.msg_list = []
        greeting_message = Message("Привет! Какой у вас запрос?", False)
        st.session_state.msg_list.append(greeting_message)


def reset():
    SESS_STATE.sql_chain_executor.reset()

    reset_message = Message("Контекст сброшен", False)
    st.session_state.msg_list.append(reset_message)


def on_input_change():
    query = st.session_state.user_input
    if query:
        query_message = Message(query, True)
        st.session_state.msg_list.append(query_message)

        with messages_container:
            query_message.display()

        st.session_state["input_text"] = ""

        answer, df = SESS_STATE.sql_chain_executor.run(query).get_all()

        answer_message = Message(answer, False)
        st.session_state.msg_list.append(answer_message)

        table = Table(df)
        st.session_state.msg_list.append(table)

        with messages_container:
            message(answer_message.text, answer_message.is_user, key=uuid.uuid4().hex)
            st.table(df)


initialize()

with messages_container:
    reprint_messages_from_msg_list()

with st.container():
    st.text_input("Ваш запрос", "", on_change=on_input_change, key="user_input")
    st.button("Сбросить контекст", on_click=reset)
    st.write(
        "История сообщений: "
        + str(SESS_STATE.sql_chain_executor.get_chat_history_size())
        + " токенов из ~16K"
    )
