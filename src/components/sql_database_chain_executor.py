import json
import logging
import pandas as pd
import langchain
import dataclasses

from langchain.callbacks import StdOutCallbackHandler
from langchain_experimental.sql import SQLDatabaseChain
from components.custom_memory import CustomMemory, HumanMessage, AiMessage


@dataclasses.dataclass
class IntermediateSteps:
    input: str | None
    top_k: int | None
    dialect: str | None
    table_info: str | None
    sql_query: str | None
    sql_result: list[dict] | None
    verbose_result: str | None

    @classmethod
    def from_chain_steps(cls, steps: list):
        if steps:
            desc = steps[0] if len(steps) > 0 else {}
            sql_query = steps[1] if len(steps) > 1 else None
            sql_result = steps[3] if len(steps) > 3 else None
            verbose_result = steps[5] if len(steps) > 5 else None
            return cls(
                input=desc.get("input"),
                top_k=desc.get("top_k"),
                dialect=desc.get("dialect"),
                table_info=desc.get("table_info"),
                sql_query=sql_query,
                sql_result=sql_result,
                verbose_result=verbose_result,
            )
        return None


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
                self.last_intermediate_steps = IntermediateSteps.from_chain_steps(
                    db_chain_response.get("intermediate_steps", None)
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

    def get_df(self) -> pd.DataFrame | None:
        steps = self.get_last_intermediate_steps()
        df = pd.DataFrame(
            steps.sql_result,
            columns=steps.sql_result[0].keys() if steps.sql_result else None,
        )

        return df

    def get_all(self) -> tuple[str, pd.DataFrame | None]:
        return self.get_answer(), self.get_df()

    def get_chat_history_size(self) -> int:
        return self.db_chain.llm_chain.llm.get_num_tokens(self.memory.get_memory())

    def get_last_intermediate_steps(self) -> IntermediateSteps:
        return self.last_intermediate_steps

    def reset(self) -> None:
        self.memory.reset()
