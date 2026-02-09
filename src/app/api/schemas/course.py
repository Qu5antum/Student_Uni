from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    section_id: int
