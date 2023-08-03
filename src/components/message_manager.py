from components.message import Message, SimpleText, SqlCode, Table
from models.intermediate_steps import IntermediateSteps


class MessageManager:
    @classmethod
    def create_answer_message(cls, answer, intermediate_steps: IntermediateSteps, df):
        return Message(
            [
                SimpleText(answer),
                SqlCode(intermediate_steps.sql_query),
                Table(df),
            ],
            is_user=False
        )
