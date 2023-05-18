import streamlit as st

from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI

db_uri = st.secrets.DB_URI
openai_api_key = st.secrets.OPENAI_API_KEY

open_ai = OpenAI(temperature=0, openai_api_key=openai_api_key)

db = SQLDatabase.from_uri(db_uri)
toolkit = SQLDatabaseToolkit(llm=open_ai, db=db)

agent = create_sql_agent(
    llm=open_ai,
    toolkit=toolkit,
    verbose=False
)