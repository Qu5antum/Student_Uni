from pydantic import BaseModel
from enum import Enum
from typing import Optional

from .user import StudentOut

class EnrollmentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExamType(str, Enum):
    MIDTERM = "MIDTERM"
    FINAL = "FINAL"


class EnrollmentOut(BaseModel):
    midterm_grade: Optional[float]
    final_grade: Optional[float]
    grade: Optional[float]
    student: StudentOut

    class Config:
        from_attributes = True
