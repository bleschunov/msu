import json
import logging
import pandas as pd
import langchain
import re
from typing import Optional, Dict, List, Tuple

from dataclasses import dataclass
from langchain import SQLDatabaseChain
from components.custom_memory import CustomMemory, HumanMessage, AiMessage


@dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    chain_answer: dict = None
    debug: bool = False
    langchain_debug: bool = False
    verbose: bool = False
    return_intermediate_steps: bool = False

    def __post_init__(self):
        langchain.debug = self.langchain_debug
        self.db_chain.verbose = self.verbose
        self.db_chain.return_intermediate_steps = self.return_intermediate_steps
        self.last_intermediate_steps = None

    @staticmethod
    def _parse_table_from_str(text):
        pattern_replacement = (
            (r"(?<=[[ ])\((?=')", "["),
            (r"(?<=\))\)", "]"),
            (r"\'", '"'),
        )
        text_mod = text
        for pattern, repl in pattern_replacement:
            text_mod = re.sub(pattern, repl, text_mod)
        return json.loads(text_mod)

    def run(self, query):
        query_with_chat_history = self.memory.get_memory() + query
        try:
            if self.return_intermediate_steps:
                r = self.db_chain(query_with_chat_history)
                chain_answer = r.get("result", None)
                self.last_intermediate_steps = r.get("intermediate_steps", None)
            else:
                chain_answer = self.db_chain.run(query_with_chat_history)
        except Exception as e:
            logging.error(e)
            chain_answer = "Произошла ошибка"

        if self.debug:
            print("Final query:\n" + query_with_chat_history)
            print("\n=====\n")
            print(f"Chat history size: {self.get_chat_history_size()} tokens")
            print("\n=====\n")
            print("Final answer:\n" + chain_answer)
            print("\n=====\n")

        self.memory.add_message(HumanMessage(query)).add_message(
            AiMessage(chain_answer)
        )
        try:
            self.chain_answer = json.loads(chain_answer)
        except json.JSONDecodeError:
            self.chain_answer = {
                "Answer": chain_answer if isinstance(chain_answer, str) else None
            }

        return self

    def get_answer(self) -> Optional[str | None]:
        if isinstance(self.chain_answer, dict):
            return self.chain_answer.get("Answer")
        else:
            return self.chain_answer

    def get_df(self) -> Optional[pd.DataFrame | None]:
        sqlres = self.chain_answer.get("SQLResult")
        return (
            pd.DataFrame(sqlres)
            if sqlres and isinstance(sqlres, (dict, list))
            else None
        )

    def get_all(self) -> Tuple[Optional[str | None], Optional[pd.DataFrame | None]]:
        return self.get_answer(), self.get_df()

    def get_chat_history_size(self) -> int:
        return self.db_chain.llm_chain.llm.get_num_tokens(self.memory.get_memory())

    def get_last_intermediate_steps(self) -> List[Optional[Dict | str]]:
        return self.last_intermediate_steps

    def reset(self) -> None:
        self.memory.reset()
