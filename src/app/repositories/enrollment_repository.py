from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List

from src.app.database.models import Enrollment, User
from src.app.api.schemas.enrollment import EnrollmentStatus
from .base_repository import BaseRepository


class EnrollmentRepository(BaseRepository):
    model = Enrollment

    async def delete_with_student_id(self, student_id: UUID):
        result = await self.session.execute(
            delete(self.model)
            .where(self.model.student_id == student_id)
            .returning(self.model.id)
        )

        return result.scalars().all()

    async def delete_course_of_students(self, student_ids: List[UUID]):
        result = await self.session.execute(
            delete(self.model)
            .where(self.model.student_id.in_(student_ids))
            .returning(self.model.id)
        )
        return result.scalars().all()
    
    async def delete_with_student_id_and_course_id(self, student_id: UUID, course_id: int):
        result = await self.session.execute(
            delete(self.model).where(
                self.model.student_id == student_id,
                self.model.course_id == course_id
            ).returning(self.model.id)
        )

        return result.scalars().all()
    
    async def get_enrollment_with_student_id_course_id(self, course_id: int, student_id: str | None = None):
        query = (
            select(self.model)
            .where(self.model.course_id == course_id)
            .options(selectinload(self.model.student))
        )

        if student_id:
            query = query.where(User.student_id == student_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        result = await self.session.execute(query)
        return result.scalars().all()
    

    async def check_student_course_with_course_id(self, course_id: int, student_id: UUID):
        """
        Check if student have this course with course id.
        """
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.student_id == student_id,
                self.model.course_id == course_id
            )
        )

        return result.scalar_one_or_none()
    
