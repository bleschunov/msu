import json
import pandas as pd

"""
Принимает на вход json файл вида
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
Отдает xlsx
"""

INPUT_JSON_FILENAME = "src/tools/interrogation_log.json"
OUTPUT_XLSX_FILENAME = "src/tools/interrogation_log.xlsx"

with open(INPUT_JSON_FILENAME, "r") as f:
    d = json.load(f)

df = pd.DataFrame.from_dict(d, "index")

df.to_excel(OUTPUT_XLSX_FILENAME)
