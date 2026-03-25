from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.app.security.security_context import hash_password
from .base_repository import BaseRepository
from src.app.database.models import User, Faculty, Section, Role, Enrollment, Course


class UserRepository(BaseRepository):
    model = User

    async def get_user_from_email(self, email: str):
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user(self, user_id: UUID):
        result = await self.session.execute(
            select(self.model).where(self.model.id == user_id)
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
    
    async def get_student_with_courses(self, student_id: UUID):
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
            .options(selectinload(self.model.teaching_courses).selectinload(Course.sections))
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
    
    async def get_teachers(self):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.roles)
            .where(Role.name == "TEACHER")
        )
        
        return result.scalars().unique().all()
    
    async def get_teacher(self, teacher_id: UUID, course_id: int | None = None):
        query = (
            select(self.model)
            .join(self.model.roles)
            .where(
                self.model.id == teacher_id,
                Role.name == "TEACHER"
            )
        )

        if course_id:
            query = query.where(self.model.teaching_courses.any(Course.id == course_id))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_students(
            self, 
            faculty_id: int | None = None,
            section_id: int | None = None,
            name: str | None = None, 
            surname: str | None = None, 
            course_id: int | None = None
    ):
        query = (
            select(self.model)
            .join(self.model.roles)
            .where(Role.name == "STUDENT")
        )

        if name and surname:
            query = query.where(
                self.model.name == name,
                self.model.surname == surname
            )

            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        
        if faculty_id and section_id:
            query = query.where(
                self.model.faculty_id == faculty_id,
                self.model.section_id == section_id
            )

            result = await self.session.execute(query)
            return result.scalars().all()

        if course_id:
            query = query.where(self.model.enrollments.any(Course.id == course_id))
        
        result = await self.session.execute(query)
        return result.scalars().unique().all()
    
    async def get_student_with_student_id(self, student_id: str):
        result = await self.session.execute(
            select(self.model).where(self.model.student_id == student_id)
        )

        return result.scalar_one_or_none()
    
    async def get_user_with_face_encode(self):
        result = await self.session.execute(
            select(self.model).where(self.model.face_encoding.is_not(None))
        )

        return result.scalars().all()
    
    async def check_teacher_course(self, teacher_id: UUID, course_id: int):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.teaching_courses)
            .where(
                self.model.id == teacher_id,
                Course.id == course_id
            )
        )

        return result.scalar_one_or_none()
    

    async def check_student_course_with_course_id(self, course_id: int, student_id: UUID):
        """
        Check if student have this course with course id.
        """
        result = await self.session.execute(
            select(self.model.id)
            .join(self.model.enrollments)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id
            )
        )

        return result.scalar_one_or_none()