import os
from supabase import create_client, Client

from components.chain import db_chain
from components.custom_memory import custom_memory
from components.message import SimpleText, SqlCode, Table
from components.sql_database_chain_executor import SQLDatabaseChainExecutor
from testing.models.question import Question
from testing.models.test import Test

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

sql_chain_executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=False, return_intermediate_steps=True
)


def ask_question(question: str, test_id: int = None):
    try:
        sql_chain_executor.run(question)
        exception = None
    except Exception as e:
        exception = e

    answer = sql_chain_executor.get_answer()
    intermediate_steps = sql_chain_executor.get_last_intermediate_steps()
    df = sql_chain_executor.get_df()

    question_object = Question(
        question=question,
        answer=SimpleText(answer).get(),
        sql=SqlCode(intermediate_steps[1] if intermediate_steps else None).get(),
        table=Table(df).get(),
        is_exception=False,
        exception=exception,
        test_id=test_id
    )

    supabase.table("question").insert(question_object.get_obj()).execute()

    sql_chain_executor.reset()


if __name__ == "__main__":
    with open("./questions.txt") as f:
        questions = f.read().splitlines()

    test_object = Test(
        name="gpt-4",
        description="",
        created_by="bleschunov"
    )

    # test = ('data', [{'id': 2, 'name': 'test 1', 'created_at': '2023-07-27T13:16:25.494123+00:00', 'created_by': 'bleschunov', 'description': 'First test'}])
    test, count = supabase.table("test").insert(test_object.get_obj()).execute()

    for i, question in enumerate(questions):
        print(str(round(i / len(questions) * 100)) + "%")
        current_test_id = test[1][0]["id"]
        ask_question(question, current_test_id)
