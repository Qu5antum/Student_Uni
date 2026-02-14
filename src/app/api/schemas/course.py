from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    course_code: str = Field(min_length=1, max_length=10)
    course_semester: str = Field(min_length=2, max_length=20)
    course_class: int = Field(ge=1, le=7)
    is_optional: bool = Field(default=True)
    section_id: int



