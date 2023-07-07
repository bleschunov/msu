import os
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI

# Создаём подключение к БД
# include_tables используем для указания таблиц, с которыми хотим работать
db = SQLDatabase.from_uri(os.getenv("DB_URI"), include_tables=["test"])

# Создаём ЛЛМ–модель для работы цепочки для работы с SQL
# -1 указывает, что лимит токенов будет подстраиватья под запрос динамически
llm = ChatOpenAI(temperature=0, verbose=False, max_tokens=512)

# Создаём цепочку для работы с SQL
# use_query_checker используем для обработки неправильно составленных SQL запросов
# Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы
db_chain = SQLDatabaseChain.from_llm(
    llm, db, verbose=True, use_query_checker=False
)
