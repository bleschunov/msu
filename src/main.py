import uuid
from dataclasses import dataclass
from typing import List

import streamlit as st
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

    def __post_init__(self):
        self.key = uuid.uuid4().hex

    def make_st_message(self, key=None):
        message(self.text, self.is_user, key=self.key if not key else key)


def reprint_messages_from_msg_list():
    for n, msg in enumerate(st.session_state.msg_list):
        msg.make_st_message(n)


def initialize():
    if not SESS_STATE:
        # slow imports made here
        from chain import db_chain
        SESS_STATE.sql_chain_executor = SQLDatabaseChainExecutor(
            db_chain, custom_memory, debug=False)

        st.session_state.msg_list: List[Message] = []
        greeting_message = Message('Привет! Какой у вас запрос?', False)
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
            query_message.make_st_message()

        st.session_state["input_text"] = ""

        answer = SESS_STATE.sql_chain_executor.run(query)
        answer_message = Message(answer, False)
        st.session_state.msg_list.append(answer_message)


initialize()

with messages_container:
    reprint_messages_from_msg_list()

with st.container():
    st.text_input('Ваш запрос', '',
                  on_change=on_input_change, key='user_input')

    st.button("Сбросить контекст", on_click=reset)
    st.write("История сообщений: " +
             str(SESS_STATE.sql_chain_executor.get_chat_history_size()) + " токенов из ~16K")
