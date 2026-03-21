from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, ForeignKey, Boolean, LargeBinary, DateTime
import sqlalchemy as sa
from typing import List, Optional
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy import Enum as SqlEnum

from .db import Base
from src.app.api.schemas.enrollment import EnrollmentStatus


user_courses = sa.Table(
    "user_courses",
    Base.metadata,
    sa.Column("user_id", ForeignKey("users.id"), primary_key=True),
    sa.Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

user_roles = sa.Table(
    "user_roles",
    Base.metadata,
    sa.Column("user_id", ForeignKey("users.id"), primary_key=True),
    sa.Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

section_courses = sa.Table(
    "section_courses",
    Base.metadata,
    sa.Column("section_id", ForeignKey("sections.id"), primary_key=True),
    sa.Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    student_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    class_: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    face_encoding: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=True)

    faculty_id: Mapped[Optional[int]] = mapped_column(ForeignKey("faculties.id"), nullable=True)
    section_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sections.id"), nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users"
    )

    faculty: Mapped["Faculty"] = relationship(back_populates="users")
    section: Mapped["Section"] = relationship(back_populates="users")

    teaching_courses: Mapped[List["Course"]] = relationship(
        secondary=user_courses,
        back_populates="teachers"
    )

    enrollments: Mapped[List["Enrollment"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles"
    )
    

class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    users: Mapped[List["User"]] = relationship(back_populates="faculty")

    sections: Mapped[List["Section"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    faculty: Mapped["Faculty"] = relationship(
        back_populates="sections"
    )
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))

    courses: Mapped[List["Course"]] = relationship(
        secondary=section_courses,
        back_populates="sections",
    )

    users: Mapped[List["User"]] = relationship(back_populates="section")

    __table_args__ = (
        sa.UniqueConstraint("name", "faculty_id"),
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    course_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    course_semester: Mapped[str] = mapped_column(String, nullable=False)
    course_class: Mapped[int] = mapped_column(Integer, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=True)

    section: Mapped[List["Course"]] = relationship(
        secondary=section_courses,
        back_populates="courses"
    )

    enrollments: Mapped[List["Enrollment"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )

    teachers: Mapped[List["User"]] = relationship(
        secondary=user_courses,
        back_populates="teaching_courses"
    )



class Enrollment(Base):
    __tablename__ = "enrollments"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grade: Mapped[float | None] = mapped_column(nullable=True)
    attempts: Mapped[int] = mapped_column(
        Integer,
        server_default="1",
        nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    status: Mapped[EnrollmentStatus] = mapped_column(
        SqlEnum(EnrollmentStatus, name="enrollment_status"),
        default=EnrollmentStatus.IN_PROGRESS
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    student: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    __table_args__ = (
        sa.UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

