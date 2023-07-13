import uuid

import pandas as pd
import streamlit as st
from dataclasses import dataclass
from streamlit_chat import message

from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

SESS_STATE = st.session_state
messages_container = st.container()


@dataclass
class Message:
    text: str
    is_user: bool
    key: str = None
    table: pd.DataFrame = None
    sql_query: str = None

    def __post_init__(self):
        self.key = uuid.uuid4().hex

    def display(self):
        text = self.text
        if self.sql_query:
            text += "\n" + f"~~~sql\n{self.sql_query}\n~~~"
        if self.table is not None:
            text += "\n" + self.table.to_markdown(index=False, floatfmt=".3f")

        message(text, self.is_user, key=self.key)


def reprint_messages_from_msg_list():
    for msg in st.session_state.msg_list:
        msg.display()


def initialize():
    if not SESS_STATE:
        # slow imports made here
        from chain import db_chain

        SESS_STATE.sql_chain_executor = SQLDatabaseChainExecutor(
            db_chain, custom_memory, debug=False, return_intermediate_steps=True
        )

        SESS_STATE.msg_list = []
        greeting_message = Message("Привет! Какой у вас запрос?", False)
        SESS_STATE.msg_list.append(greeting_message)


def reset():
    SESS_STATE.sql_chain_executor.reset()

    reset_message = Message("Контекст сброшен", False)
    st.session_state.msg_list.append(reset_message)


def on_input():
    query = st.session_state.user_input
    if query:
        query_message = Message(query, True)
        st.session_state.msg_list.append(query_message)

        with messages_container:
            query_message.display()

        st.session_state["input_text"] = ""

        answer, df = SESS_STATE.sql_chain_executor.run(query).get_all()

        intermediate_steps = SESS_STATE.sql_chain_executor.get_last_intermediate_steps()
        answer_message = Message(
            answer, False, table=df, sql_query=intermediate_steps[1]
        )
        st.session_state.msg_list.append(answer_message)

        with messages_container:
            answer_message.display()


initialize()

with messages_container:
    reprint_messages_from_msg_list()

with st.container():
    with st.form("query_form", clear_on_submit=True):
        st.text_input("Ваш запрос", "", key="user_input")
        submitted = st.form_submit_button("Отправить")
        if submitted:
            on_input()

    st.button("Сбросить контекст", on_click=reset)
    st.write(
        "История сообщений: "
        + str(SESS_STATE.sql_chain_executor.get_chat_history_size())
        + " токенов из ~16K"
    )
