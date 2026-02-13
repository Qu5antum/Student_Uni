from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    section_id: int



