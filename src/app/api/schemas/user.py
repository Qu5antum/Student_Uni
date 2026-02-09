from pydantic import BaseModel, Field, field_validator
from typing import List
import string

class StudentCreate(BaseModel):
    student_id: int
    name: str  = Field(min_length=2, max_length=18)
    surname: str = Field(min_length=2, max_length=18)
    class_: int
    password: str = Field(min_length=7, max_length=15)
    faculty_id: int
    section_id: int
    #role: List[str]

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
    name: str  = Field(min_length=2, max_length=18)
    surname: str = Field(min_length=2, max_length=18)
    password: str = Field(min_length=7, max_length=15)
    #role: List[str]

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


