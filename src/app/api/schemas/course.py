from pydantic import BaseModel, Field, EmailStr
from typing import List
from uuid import UUID

class CourseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    course_code: str = Field(min_length=1, max_length=10)
    course_semester: str = Field(min_length=2, max_length=20)
    course_class: int = Field(ge=1, le=7)
    is_optional: bool = Field(default=False)
    section_id: int


class CourseUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    course_code: str | None = Field(None, min_length=1, max_length=10)
    course_semester: str | None = Field(None, min_length=2, max_length=20)
    course_class: int | None = Field(None, ge=1, le=7)
    is_optional: bool | None = None
    section_id: int | None = None


class CourseOut(BaseModel):
    id: int
    name: str
    course_code: str
    course_semester: str
    course_class: int
    is_optional: bool
    section_id: int

    class Config:
        from_attributes = True

class StudentCoursesOut(BaseModel):
    id: UUID
    name: str
    surname: str
    email: EmailStr
    student_id: str
    class_: int
    faculty_id: int
    section_id: int
    courses: List[CourseOut]

    class Config:
        from_attributes = True


class TeacherCoursesOut(BaseModel):
    id : UUID
    name: str
    surname: str
    email: EmailStr
    faculty_id: int
    courses: List[CourseOut]

    class Config:
        from_attributes = True

