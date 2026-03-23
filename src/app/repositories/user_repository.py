from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.app.security.security_context import hash_password
from .base_repository import BaseRepository
from src.app.database.models import User, Faculty, Section, Role, Enrollment


class UserRepository(BaseRepository):
    model = User

    async def get_user_from_email(self, email: str):
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def get_student_profile(self, user_id: UUID):
        result = await self.session.execute(
            select(
                self.model.name,
                self.model.surname,
                self.model.email,
                self.model.student_id,
                self.model.class_,
                Faculty.name.label("faculty_name"), 
                Section.name.label("section_name")
            )
            .join(self.model.roles)
            .join(self.model.faculty)
            .join(self.model.section)
            .where(
                self.model.id == user_id,
                Role.name == "STUDENT"
            )
        )

        return result.mappings().one_or_none()
    
    async def get_teacher_profile(self, user_id: UUID):
        result = await self.session.execute(
            select(
                self.model.name,
                self.model.surname,
                self.model.email,
                Faculty.name.label("faculty_name"), 
            )
            .join(self.model.roles)
            .join(self.model.faculty)
            .where(
                self.model.id == user_id,
                Role.name == "TEACHER"
            )
        )

        return result.mappings().one_or_none()
    
    async def update_password(self, user_id: UUID, new_password: str):
        result = await self.session.execute(
            select(self.model).where(self.model.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.password = hash_password(new_password)
        await self.session.commit()
        await self.session.refresh(user)

        return user
    
    async def get_student_with_courses(self, student_id: str):
        result = await self.session.execute(
            select(self.model)
            .where(self.model.student_id == student_id)
            .options(
                selectinload(self.model.enrollments).selectinload(Enrollment.course)
            )
        )

        return result.scalar_one_or_none()
    
    async def count_student_in_course(self, course_id: int):
        result = await self.session.execute(
            select(func.count(func.distinct(self.model.id)))
            .join(self.model.roles)
            .join(self.model.enrollments)
            .where(
                Enrollment.course_id == course_id,
                Role.name == "STUDENT"
            )
        )

        return result.scalar_one()
    
    async def get_student_with_section_id(self, section_id: int):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.roles)
            .where(
                Role.name == "STUDENT",
                self.model.section_id == section_id,
            )
            .options(selectinload(self.model.enrollments).selectinload(Enrollment.course))
        )
        return result.scalars().all()
    
    async def get_teacher_with_courses(self, teacher_id: UUID):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.roles)
            .where(
                self.model.id == teacher_id,
                Role.name == "TEACHER"
            )
            .options(selectinload(self.model.teaching_courses))
        )

        return result.scalar_one_or_none()
    
    async def get_teachers_with_courses_in_section(self, section_id: int):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.roles)
            .where(
                Role.name == "TEACHER",
                self.model.section_id == section_id
            )
            .options(selectinload(self.model.teaching_courses))
        )
        return result.scalars().all()


        
        

