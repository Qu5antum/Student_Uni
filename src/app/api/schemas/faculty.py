from pydantic import BaseModel, Field


class FacultyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=18)