import json

from chain import db_chain
from custom_memory import custom_memory
from sql_database_chain_executor import SQLDatabaseChainExecutor

"""
Опрашивает языковую модель по вопросам через новую строку из txt файла. Сохраняет результат в json вида:
{
    "0": {
        "user_input": "Сколько заработала компания за прошлый месяц",
        "answer": "Сколько заработала компания за прошлый месяц\nSQLQuery: SELECT SUM([Сумма договора]) AS TotalEarnings\nFROM test\nWHERE [Период] = FORMAT(DATEADD(MONTH, -1, CAST(GETDATE() AS date)), 'yyyy-MM')",
        "sql_query": "SELECT SUM([Сумма договора]) AS TotalEarnings\nFROM test\nWHERE [Период] = FORMAT(DATEADD(MONTH, -1, CAST(GETDATE() AS date)), 'yyyy-MM')",
        "excepted": false,
        "exception": null
    },
    "1": {
        "user_input": "Сколько чистой прибыли принесла компания ФСК",
        "answer": "Чистая прибыль компании ФСК не принесла прибыли.",
        "sql_query": "SELECT SUM([Сумма]) AS [Чистая прибыль]\nFROM test\nWHERE [Тип документа] = 'Списание'\nAND [Статья движения денежных средств] = 'Оплата'\nAND [Назначение платежа] LIKE '%чистая прибыль%'\nAND [План/Факт] = 'Факт'\nAND [Сумма] > 0",
        "excepted": false,
        "exception": null
    },
}
"""

INPUT_TXT_FILENAME = "src/utils/questions.txt"
OUTPUT_JSON_FILENAME = "src/utils/interrogation_log.json"

executor = SQLDatabaseChainExecutor(
    db_chain, custom_memory, debug=False, verbose=False, return_intermediate_steps=True
)

d = {}

with open(INPUT_TXT_FILENAME, "r") as f:
    for n, line in enumerate(f.readlines()):
        user_input = line.strip()
        answer = None
        sql_query = None
        excepted = False
        exception = None
        print(f'{n}. Question "{user_input}"')
        try:
            executor.reset()
            answer = executor.run(user_input)
            print(f"Question {user_input} successful")

        except Exception as e:
            print(f"Question {user_input} excepted")
            excepted = True
            exception = e.args[0]
        sql_query = executor.get_last_intermediate_steps[1]
        d[n] = {
            "user_input": user_input,
            "answer": answer,
            "sql_query": sql_query,
            "excepted": excepted,
            "exception": exception,
        }

s = json.dumps(d, ensure_ascii=False, indent=4)
with open(OUTPUT_JSON_FILENAME, "w") as f:
    f.write(s)
print(f"Saved to {OUTPUT_JSON_FILENAME}")
