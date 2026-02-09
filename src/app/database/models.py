from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
import sqlalchemy as sa
from typing import List
from .db import Base


user_courses = sa.Table(
    "user_courses",
    Base.metadata,
    sa.Column("user_id", ForeignKey("users.id"), primary_key=True),
    sa.Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    class_: Mapped[int] = mapped_column(Integer)
    password: Mapped[str] = mapped_column(String)

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users"
    )

    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))

    faculty: Mapped["Faculty"] = relationship(back_populates="users")
    section: Mapped["Section"] = relationship(back_populates="users")

    courses: Mapped[list["Course"]] = relationship(
        secondary=user_courses,
        back_populates="users"
    )



class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
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
        back_populates="section",
        cascade="all, delete-orphan"
    )

    users: Mapped[List["User"]] = relationship(back_populates="section")

    __table_args__ = (
        sa.UniqueConstraint("name", "faculty_id"),
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    section: Mapped["Section"] = relationship(
        back_populates="courses"
    )
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))

    users: Mapped[list["User"]] = relationship(
        secondary=user_courses,
        back_populates="courses"
    )

    __table_args__ = (
        sa.UniqueConstraint("name", "section_id"),
    )

