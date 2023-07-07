from dataclasses import dataclass

import langchain
from langchain import SQLDatabaseChain
from custom_memory import CustomMemory, HumanMessage, AiMessage


@dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    debug: bool = False

    def __post_init__(self):
        langchain.debug = self.debug

    def run(self, query):
        query = self.memory.get_memory() + query
        chain_answer = self.db_chain.run(query)
        self.memory\
            .add_message(HumanMessage(query))\
            .add_message(AiMessage(chain_answer))

        if self.debug:
            print("Final query:\n" + query)

        return chain_answer
