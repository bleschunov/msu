import os
from dataclasses import dataclass

import langchain

from langchain import SQLDatabase, PromptTemplate, OpenAI, SQLDatabaseChain

from custom_memory import CustomMemory, HumanMessage, AiMessage
from prompt import input_variables, _DEFAULT_TEMPLATE

langchain.debug = False


def get_chat_history(memory):
    return "Here is chat history:\n" + memory.load_memory_variables({})["chat_history"] + "\n"


# Создаём кастомный промпт для SQL–цепочки
prompt_template = PromptTemplate(
    input_variables=input_variables, template=_DEFAULT_TEMPLATE
)

# Создаём память, чтобы бот мог общаться в контексте всего диалога
custom_memory = CustomMemory()

# Создаём подключение к БД
# include_tables используем для указания таблиц, с которыми хотим работать
db = SQLDatabase.from_uri(os.getenv("DB_URI"), include_tables=["test"])

# Создаём ЛЛМ–модель для работы цепочки для работы с SQL
llm = OpenAI(temperature=0, verbose=False, max_tokens=256)

# Создаём цепочку для работы с SQL
# use_query_checker используем для обработки неправильно составленных SQL запросов
# Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы
db_chain = SQLDatabaseChain.from_llm(
    llm, db, verbose=True, use_query_checker=True
)


@dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    debug: bool = False

    def run(self, query):
        query = custom_memory.get_memory() + query

        if self.debug:
            print("Final query:\n" + query)

        chain_answer = self.db_chain.run(query)
        self.memory\
            .add_message(HumanMessage(query))\
            .add_message(AiMessage(chain_answer))
        return chain_answer


executor = SQLDatabaseChainExecutor(db_chain, custom_memory, debug=True)

print(executor.run("Топ 5 компаний по чистой прибыли за 2023 год"))
print(executor.run("Кто из них принес больше всего прибыли?"))
# print(memory.load_memory_variables({}))
