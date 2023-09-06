import uuid

import streamlit as st
from streamlit_chat import message

from components.supabase_repository import supabase_repository

st.set_page_config(layout="wide")

(_, test_sets), _ = supabase_repository.select_test_sets()


def find_test_set_id_by_name(name: str) -> int:
    return [test_set["id"] for test_set in test_sets if test_set["name"] == name][0]


def get_test_set_names() -> tuple:
    return tuple(test_set["name"] for test_set in test_sets)


def find_test_by_question(question: str, tests: list[dict]) -> dict | None:
    found = [test for test in tests if test["question"] == question]

    if len(found) == 0:
        return None

    return found[0]


def get_merged_answers(tests_a: list[dict], tests_b: list[dict]) -> list[tuple]:
    result = []
    for test_a in tests_a:
        test_b = find_test_by_question(test_a["question"], tests_b)
        result.append((test_a, test_b))

    return result


def create_case(answer: dict | None):
    if answer is None:
        return

    message(answer["question"], is_user=True, key=uuid.uuid4().hex)

    answer_content = "\n".join(filter(lambda x: x is not None, [answer["answer"], answer["sql"], answer["table"]]))
    message(answer_content, is_user=False, key=uuid.uuid4().hex)


with st.container() as container:
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Выберите первый тест для сравнения",
            get_test_set_names(),
            key="first_test_set_name"
        )

        (_, first_tests), _ = supabase_repository.select_test_by_test_set_id(
                find_test_set_id_by_name(st.session_state.first_test_set_name)
            )

    with col2:
        st.selectbox(
            "Выберите первый тест для сравнения",
            get_test_set_names(),
            key="second_test_set_name"
        )

        (_, second_tests), _ = supabase_repository.select_test_by_test_set_id(
                find_test_set_id_by_name(st.session_state.second_test_set_name)
            )

    merged_answers = get_merged_answers(first_tests, second_tests)


for first_test, second_test in merged_answers:
    with st.container() as container:
        col1, col2 = st.columns(2)

        with col1:
            create_case(first_test)

        with col2:
            create_case(second_test)
