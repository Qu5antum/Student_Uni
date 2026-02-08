from pydantic import BaseModel


class UserCreate(BaseModel):
    student_id: int
    name: str
    surname: str
    class_: str


