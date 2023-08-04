import streamlit as st

from components.chain import get_db, get_llm
from components.message import SimpleText, Message
from components.sql_database_chain_executor import get_sql_database_chain_executor
from components.message_manager import MessageManager

SESS_STATE = st.session_state
messages_container = st.container()


def reprint_messages_from_msg_list():
    for msg in st.session_state.msg_list:
        msg.display()


def initialize():
    if not SESS_STATE:
        SESS_STATE.sql_database_chain_executor = get_sql_database_chain_executor(
            get_db(),
            get_llm(model_name="gpt-3.5-turbo-16k"),
            debug=False,
            return_intermediate_steps=True
        )

        SESS_STATE.msg_list = []
        greeting_message = Message(
            [SimpleText("Привет! Какой у вас запрос?")], is_user=False
        )
        SESS_STATE.msg_list.append(greeting_message)


def reset():
    SESS_STATE.sql_database_chain_executor.reset()

    reset_message = Message([SimpleText("Контекст сброшен")], is_user=False)
    st.session_state.msg_list.append(reset_message)


def on_input():
    query = st.session_state.user_input
    if query:
        query_message = Message([SimpleText(query)], is_user=True)
        st.session_state.msg_list.append(query_message)

        with messages_container:
            query_message.display()

        st.session_state["input_text"] = ""

        SESS_STATE.sql_database_chain_executor.run(query)

        answer = SESS_STATE.sql_database_chain_executor.get_answer()
        intermediate_steps = SESS_STATE.sql_database_chain_executor.get_last_intermediate_steps()
        df = SESS_STATE.sql_database_chain_executor.get_df()

        answer_message = MessageManager.create_answer_message(answer, intermediate_steps, df)
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

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            "Если получаете в выдаче компании с пустым названием, попробуйте добавить в запрос слова: «Не учитывай NULL»"
        )

    with col2:
        st.button("Сбросить контекст", on_click=reset)

    st.write(
        "История сообщений: "
        + str(SESS_STATE.sql_database_chain_executor.get_chat_history_size())
        + " токенов из ~16K"
    )
