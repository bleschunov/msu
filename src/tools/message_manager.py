from components.message import Message, SimpleText, SqlCode, Table


class MessageManager:
    @classmethod
    def create_answer_message(cls, answer, intermediate_steps, df):
        return Message(
            [
                SimpleText(answer),
                SqlCode(intermediate_steps[1] if intermediate_steps else None),
                Table(df),
            ],
            is_user=False
        )
