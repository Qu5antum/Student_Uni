from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from src.app.database.models import Course, Section, Enrollment
from .base_repository import BaseRepository
from src.app.api.schemas.enrollment import EnrollmentStatus


class CourseRepository(BaseRepository):
    model = Course

    async def get_course_by_code(self, course_code: str):
        result = await self.session.execute(
            select(self.model).where(self.model.course_code == course_code)
        )
            
        return result.scalar_one_or_none()
    
    async def get_course_with_section_id(self, section_id: int, course_id: int | None = None):
        query = (
            select(self.model)
            .join(self.model.sections)
            .where(Section.id == section_id)
            .options(selectinload(self.model.sections))
            .distinct()
        )

        if course_id:
            query = query.where(self.model.id == course_id)
            result = await self.session.execute(query)

            return result.scalar_one_or_none()

        result = await self.session.execute(query)

        return result.scalars().all()
    
    async def get_course_with_class_and_semester(self, student_class: int, semester: str):
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.course_class == student_class,
                self.model.course_semester == semester
            )
        )

        return result.scalars().all()
    
    async def get_courses_with_ids_and_semester(self, course_ids: List[int], semester: str):
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.id.in_(course_ids),
                self.model.course_semester == semester
            )
        )

        return result.scalars().all()
    
    async def get_course_with_id_and_semester(self, course_id: int, semester: str, student_class: int):
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.id == course_id,
                self.model.course_semester == semester,
                self.model.course_class >= student_class
            )
        )

        return result.scalar_one_or_none()
    
    async def get_optional_courses_of_student(self, student_id: UUID):
        result = await self.session.execute(
            select(self.model.id)
            .join(self.model.enrollments)
            .where(
                Enrollment.student_id == student_id,
                self.model.is_optional == "True"
            )
        )

        return result.scalars().all()


    async def failed_courses_of_student(self, student_id: UUID):
        result = await self.session.execute(
            select(self.model)
            .join(self.model.enrollments)
            .where(
                Enrollment.status == EnrollmentStatus.FAILED,
                Enrollment.student_id == student_id
            )
        )

        return result.scalars().all()