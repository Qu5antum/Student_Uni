from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List
import string
from uuid import UUID

class StudentCreate(BaseModel):
    student_id: str = Field(max_length=11)
    name: str  = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr
    class_: int
    password: str = Field(min_length=7, max_length=15)
    faculty_id: int
    section_id: int

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        if not any(i.islower() for i in password):
            raise ValueError("Password must contain at least one small letter")
        if not any(i.isupper() for i in password):
            raise ValueError("Password must contain at least one capital letter")
        if not any(i.isdigit() for i in password):
            raise ValueError("Password must contain at least one digit")
        if not any(i in string.punctuation for i in password):
            raise ValueError("Password must contain at least one punctuation")
        
        return password
    

class PersonelCreate(BaseModel):
    name: str  = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=7, max_length=15)

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        if not any(i.islower() for i in password):
            raise ValueError("Password must contain at least one small letter")
        if not any(i.isupper() for i in password):
            raise ValueError("Password must contain at least one capital letter")
        if not any(i.isdigit() for i in password):
            raise ValueError("Password must contain at least one digit")
        if not any(i in string.punctuation for i in password):
            raise ValueError("Password must contain at least one punctuation")
        
        return password
    

class UserCourse(BaseModel):
    student_id: str | None = Field(None, max_length=11)
    name: str | None = Field(None, min_length=2, max_length=50)
    surname: str | None = Field(None, min_length=2, max_length=50)


class UserOut(BaseModel):
    id: UUID
    student_id: str
    name: str
    surname: str
    class_: int
    email: EmailStr
    faculty_id: int
    section_id: int

    class Config:
        from_attributes = True




