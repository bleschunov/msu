_DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}

Note that if the question does not mention a Бюджет and План, then we will sample based on Факт.
Use TOP instead LIMIT.
When use column Контрагенты add IS NOT NULL condition on it.
Use date in the format like 2023-03-15 00:00:00.

Question: {input}"""

input_variables = ["input", "table_info", "dialect"]
