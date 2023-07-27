from dataclasses import dataclass
from datetime import datetime


@dataclass
class Test:
    name: str
    description: str | None
    created_by: str | None
    created_at: datetime | None = None
    id: int = None

    def get_obj(self):
        res = self.__dict__
        del res["id"]
        del res["created_at"]
        return res
