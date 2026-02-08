from pydantic import BaseModel


class FacultyCreate(BaseModel):
    name: str