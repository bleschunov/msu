import json
import logging
import pandas as pd
import langchain
import dataclasses

from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

from components.chain import get_sql_database_chain_patched
from components.custom_memory import CustomMemory, HumanMessage, AiMessage, custom_memory
from components.patched_database_class import SQLDatabasePatched


@dataclasses.dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    chain_answer: any = dataclasses.field(default_factory=dict)
    debug: bool = False
    langchain_debug: bool = False
    verbose: bool = False
    return_intermediate_steps: bool = False
    last_intermediate_steps: list[dict | str] = None

    def __post_init__(self):
        langchain.debug = self.langchain_debug
        self.db_chain.verbose = self.verbose
        self.db_chain.return_intermediate_steps = self.return_intermediate_steps

    def run(self, query):
        query_with_chat_history = self.memory.get_memory() + query

        callbacks = []
        if self.debug:
            callbacks.append(StdOutCallbackHandler())

        try:
            if self.return_intermediate_steps:
                db_chain_response = self.db_chain(query_with_chat_history, callbacks=callbacks)
                chain_answer = db_chain_response.get("result", None)
                self.last_intermediate_steps = db_chain_response.get(
                    "intermediate_steps", None
                )
            else:
                chain_answer = self.db_chain.run(
                    query_with_chat_history,
                    callbacks=callbacks
                )
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

    def get_answer(self) -> str:
        if isinstance(self.chain_answer, dict):
            return str(self.chain_answer.get("Answer"))
        else:
            return self.chain_answer

    # TODO: убрать магические числа, можно описать структуру steps, а можно взять числа в переменные с говорящими именами
    def get_df(self) -> pd.DataFrame | None:
        steps = self.get_last_intermediate_steps()
        df = (
            pd.DataFrame(
                steps[3], columns=steps[3][0].keys() if len(steps[3]) > 0 else None
            )
            if len(steps) >= 4
            else None
        )

        return df

    def get_all(self) -> tuple[str, pd.DataFrame | None]:
        return self.get_answer(), self.get_df()

    def get_chat_history_size(self) -> int:
        return self.db_chain.llm_chain.llm.get_num_tokens(self.memory.get_memory())

    def get_last_intermediate_steps(self) -> list[dict | str]:
        return self.last_intermediate_steps

    def reset(self) -> None:
        self.memory.reset()


def get_sql_database_chain_executor(
    db: SQLDatabasePatched,
    llm: ChatOpenAI,
    debug=False,
    return_intermediate_steps=True
) -> SQLDatabaseChainExecutor:
    return SQLDatabaseChainExecutor(
        get_sql_database_chain_patched(db, llm),
        custom_memory,
        debug=debug,
        return_intermediate_steps=return_intermediate_steps
    )
