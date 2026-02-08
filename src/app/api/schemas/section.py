from pydantic import BaseModel


class Section(BaseModel):
    name: str