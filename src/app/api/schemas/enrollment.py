from enum import Enum

class EnrollmentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExamType(str, Enum):
    MIDTERM = "MIDTERM"
    FINAL = "FINAL"