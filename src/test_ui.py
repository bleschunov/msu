import uuid

import streamlit as st
from streamlit_chat import message

from testing.tests import supabase

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)

tests, count = supabase.table("test").select("*").execute()
tests = {t["name"]: t["id"] for t in tests[1]}


def create_case(answer):
    message(answer["question"], is_user=True, key=uuid.uuid4().hex)

    answer_content = "\n".join([answer["answer"], answer["sql"], answer["table"]])
    message(answer_content, is_user=False, key=uuid.uuid4().hex)


with st.container() as container:
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Выберите первый тест для сравнения",
            (name for name in tests),
            key="first_test_name"
        )

        first_answers, _ = supabase.table("question").select("*")\
            .eq("test_id", tests[st.session_state.first_test_name]).execute()
        first_answers = first_answers[1]

    with col2:
        st.selectbox(
            "Выберите первый тест для сравнения",
            (name for name in tests),
            key="second_test_name"
        )

        second_answers, _ = supabase.table("question").select("*")\
            .eq("test_id", tests[st.session_state.second_test_name]).execute()
        second_answers = second_answers[1]

    merged_answers = []
    for first_answer in first_answers:
        second_answer = [a for a in second_answers if a["question"] == first_answer["question"]][0]
        merged_answers.append((first_answer, second_answer))

for first_answer, second_answer in merged_answers:
    with st.container() as container:
        col1, col2 = st.columns(2)

        with col1:
            create_case(first_answer)

        with col2:
            create_case(second_answer)
