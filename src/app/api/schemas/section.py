from pydantic import BaseModel, Field


class SectionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    faculty_id: int