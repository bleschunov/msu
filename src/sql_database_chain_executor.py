import json
import pandas as pd
import langchain

from dataclasses import dataclass
from langchain import SQLDatabaseChain
from custom_memory import CustomMemory, HumanMessage, AiMessage


@dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    chain_answer: dict = None
    debug: bool = False
    langchain_debug: bool = False
    verbose: bool = False

    def __post_init__(self):
        langchain.debug = self.langchain_debug
        self.db_chain.verbose = self.verbose

    def run(self, query):
        query_with_chat_history = self.memory.get_memory() + query
        chain_answer = self.db_chain.run(query_with_chat_history)

        if self.debug:
            print("Final query:\n" + query_with_chat_history)
            print("\n=====\n")
            print(f"Chat history size: {self.get_chat_history_size()} tokens")
            print("\n=====\n")
            print("Final answer:\n" + chain_answer)
            print("\n=====\n")

        self.memory \
            .add_message(HumanMessage(query)) \
            .add_message(AiMessage(chain_answer))

        self.chain_answer = json.loads(chain_answer)
        
        return self
    
    def get_answer(self):
        return self.chain_answer["Answer"]
    
    def get_df(self):
        return pd.DataFrame(self.chain_answer["SQLResult"])
    
    def get_all(self):
        return self.get_answer(), self.get_df()

    def get_chat_history_size(self):
        return self.db_chain.llm_chain.llm.get_num_tokens(self.memory.get_memory())

    def reset(self):
        self.memory.reset()
