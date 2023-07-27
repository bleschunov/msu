import os
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from components.custom_prompt import custom_prompt
from components.patched_sql_chain import SQLDatabaseChainPatched
from components.patched_database_class import SQLDatabasePatched

# Создаём подключение к БД
# include_tables используем для указания таблиц, с которыми хотим работать
db = SQLDatabasePatched.from_uri(os.getenv("DB_URI"), include_tables=["test"])

# Создаём ЛЛМ–модель для работы цепочки для работы с SQL
# max_tokens=-1 указывает, что лимит токенов будет подстраиватья под запрос динамически
llm = ChatOpenAI(
    temperature=0,
    verbose=False,
    max_tokens=None,
    model_name="gpt-3.5-turbo-16k"
)

# Создаём цепочку для работы с SQL
# use_query_checker используем для обработки неправильно составленных SQL запросов
# use_query_checker=False, потому что True с моделью на 16К токенов ломает чейн
# Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы

db_chain = SQLDatabaseChainPatched(
    llm=llm,
    database=db,
    prompt=custom_prompt,
    use_query_checker=False,
    return_direct=False,
)
