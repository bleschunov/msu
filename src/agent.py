import os
from langchain import SQLDatabase, SQLDatabaseChain, LLMChain, OpenAI
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

memory = ConversationBufferMemory(memory_key="chat_history")
db = SQLDatabase.from_uri(os.getenv("DB_URI"), include_tables=['test'])
print(db.table_info)
llm = OpenAI(temperature=0, verbose=True)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

tools = [
    Tool(
        name="SQL",
        func=db_chain.run,
        description="useful for when you need to extract information from database",
    )
]

prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
suffix = """Begin!"

{chat_history}
Question: {input}
{agent_scratchpad}"""

prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)

llm_chain = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt)
_agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
agent = AgentExecutor.from_agent_and_tools(
    agent=_agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True
)

print(agent.run("Сколько компания заработала за всё время?"))
