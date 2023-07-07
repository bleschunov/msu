from dataclasses import dataclass

import streamlit as st
from streamlit_chat import message

from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

executor = SQLDatabaseChainExecutor(db_chain, custom_memory, debug=True)


@dataclass
class Message:
    text: str
    is_user: bool


def print_messages():
    for msg in st.session_state.msg_list:
        message(msg.text, msg.is_user)


if "msg_list" not in st.session_state:
    st.session_state.msg_list = []

query = st.text_input('Ваш запрос', '')
if len(st.session_state.msg_list) == 0:
    st.session_state.msg_list.append(Message('Привет! Какой у вас запрос?', False))
    print_messages()
    exit()

st.session_state.msg_list.append(Message(query, True))
print_messages()

if len(st.session_state.msg_list) > 1:
    answer = executor.run(query)
    st.session_state.msg_list.append(Message(answer, False))
    message(answer)
