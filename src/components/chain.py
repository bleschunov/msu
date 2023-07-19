import os
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from components.custom_prompt import custom_prompt

# Создаём подключение к БД
# include_tables используем для указания таблиц, с которыми хотим работать
db = SQLDatabase.from_uri(os.getenv("DB_URI"), include_tables=["test"])

# Создаём ЛЛМ–модель для работы цепочки для работы с SQL
# max_tokens=-1 указывает, что лимит токенов будет подстраиватья под запрос динамически
llm = ChatOpenAI(temperature=0, verbose=False, max_tokens=512, model_name="gpt-3.5-turbo-16k")

# Создаём цепочку для работы с SQL
# use_query_checker используем для обработки неправильно составленных SQL запросов
# use_query_checker=False, потому что True с моделью на 16К токенов ломает чейн
# Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы

db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=custom_prompt, use_query_checker=False)
