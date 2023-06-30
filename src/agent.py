import os
from langchain import SQLDatabase, SQLDatabaseChain, LLMChain, OpenAI, PromptTemplate
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from prompt import _DEFAULT_TEMPLATE, input_variables

# Создаём кастомный промпт для SQL–цепочки
prompt_template = PromptTemplate(
    input_variables=input_variables, template=_DEFAULT_TEMPLATE
)

# Создаём память, чтобы бот мог общаться в контексте всего диалога
memory = ConversationBufferMemory(memory_key="chat_history")

# Создаём подключение к БД
# include_tables используем для указания таблиц, с которыми хотим работать
db = SQLDatabase.from_uri(os.getenv("DB_URI"), include_tables=['test'])

# Создаём ЛЛМ–модель для работы цепочки для работы с SQL
llm = OpenAI(temperature=0, verbose=False, model_name="gpt-3.5-turbo-16k")

# Создаём цепочку для работы с SQL
# use_query_checker используем для обработки неправильно составленных SQL запросов
# Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы
db_chain = SQLDatabaseChain.from_llm(
    llm, db, verbose=True, prompt=prompt_template, use_query_checker=True
)

# Используем SQL–цепочку в качестве инструмента для агента
tools = [
    Tool(
        name="SQL",
        func=db_chain.run,
        description="useful for when you need to extract information from database",
    ),
]

# Промпт для работы агента
prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
suffix = """Begin!"

{chat_history}
Question: {input}
{agent_scratchpad}"""

# Создаём объект промпта
prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)

# Создаём цепочку—основу для агента
llm_chain = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt)

# Создаём агента
_agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=False)

# Создаём обёртку для вызова агента
agent = AgentExecutor.from_agent_and_tools(
    agent=_agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True
)

print(agent.run("Топ 5 компаний по чистой прибыли за 2023 год"))
print(agent.run("Кто из них принес больше всего прибыли?"))

# 1. Сколько заработала компания за прошлый месяц
# 2. Сколько чистой прибыли принесла компания ФСК
# 3. Покажи доходы компании с помесячной разбивкой
# 4. Топ 10 компаний по выручке за 2023 год
# 5. Топ 5 компаний по чистой прибыли за 2023 год
# 6. Средний ежемесячный фот компании с начала 2023 года
# 7. Какому подрядчику мы заплатили больше всего денег за работы в прошлом месяце
# 8. В каком месяце были самые большие налоговые платежи
# 9. По какому казначейскому счету было самое большое движение денег за последние 4 месяца
# 10. У какой категории объектов наибольший положительный баланс в теккущем году
# 11. Топ 5 объектов с наибольшим количеством контрагентов
# 11.1 По какому из объектов наибольшее сальдо поступлений и списаний
# 12. Покажи динамику платежей на соц.страхование
# 13. Покажи договоры где сумма платежей превысила сумму по договору
# 14. Топ 10 объектов с наибольшей разницей плановых и фактических поступлений
# 14.1 Какой из объектов имеет наибольшее сальдо между поступлениями и списаниями
# 15. Топ 10 объектов с наибольшей разницей плановых и фактических поступлений
# 16. Топ 10 объектов с наибольшей разницей с наибольшей разницей планового и фактического сальдо поступлений и списаний
# 17. Дай прогноз поступлений и списаний до конца года
# 18. Топ 20 объектов по поступлениям за последние 6 месяцев
# 18.1 Кто из заказчиков принес больше всех денег
