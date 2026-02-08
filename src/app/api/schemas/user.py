from pydantic import BaseModel


class UserCreate(BaseModel):
    student_id: int
    name: str
    surname: str
    class_: str
    faculty_id: int
    section_id: int
    course_id: int


