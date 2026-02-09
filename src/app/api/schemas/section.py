from pydantic import BaseModel


class SectionCreate(BaseModel):
    name: str
    faculty_id: int