from dataclasses import dataclass


@dataclass
class Question:
    question: str
    answer: str
    sql: str
    table: str
    is_exception: bool
    exception: str | None
    test_id: int
    id: int = None

    def get_obj(self):
        res = self.__dict__
        del res["id"]
        return res
