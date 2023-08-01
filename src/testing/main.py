from components.chain import get_db, get_llm
from components.message import SimpleText, SqlCode, Table
from components.sql_database_chain_executor import get_sql_database_chain_executor
from components.supabase_repository import supabase_repository
from testing.models.test import Test
from testing.models.test_set import TestSet


TEST_SET_NAME = "gpt-4"
TEST_SET_DESCRIPTION = ""
CREATED_BY = "bleschunov"


sql_database_chain_executor = get_sql_database_chain_executor(
    get_db(tables=["test"]),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=False,
    return_intermediate_steps=True
)


def get_questions(filename: str) -> list[str]:
    with open(f"./{filename}") as f:
        return f.read().splitlines()


def display_current_progress(current_question_number: int, questions_count: int) -> None:
    # Печатает, сколько процентов вопросов обработано
    print(str(round(current_question_number / questions_count * 100)) + "%")


def get_test_results(question: str, test_id: int = None) -> Test:
    try:
        sql_database_chain_executor.run(question)
        exception = None
    except Exception as e:
        exception = e

    answer = sql_database_chain_executor.get_answer()
    intermediate_steps = sql_database_chain_executor.get_last_intermediate_steps()
    df = sql_database_chain_executor.get_df()

    test = Test(
        question=question,
        answer=SimpleText(answer).get(),
        sql=SqlCode(intermediate_steps[1] if intermediate_steps else None).get(),
        table=Table(df).get(),
        is_exception=False,
        exception=exception,
        test_id=test_id
    )

    return test


if __name__ == "__main__":
    questions = get_questions("questions.txt")
    questions_count = len(questions)

    test_set = TestSet(
        name=TEST_SET_NAME,
        description=TEST_SET_DESCRIPTION,
        created_by=CREATED_BY
    )

    # hint: test = ('data', [{'id': 2, 'name': 'test 1', 'created_at': '2023-07-27T13:16:25.494123+00:00', 'created_by': 'bleschunov', 'description': 'First test'}])
    test, count = supabase_repository.insert_test_set(test_set)
    current_test_id = test[1][0]["id"]

    for current_question_number, question in enumerate(questions):
        display_current_progress(current_question_number, questions_count)
        supabase_repository.insert_test(get_test_results(question, current_test_id))
        sql_database_chain_executor.reset()
