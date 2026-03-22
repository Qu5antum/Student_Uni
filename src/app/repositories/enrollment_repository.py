from sqlalchemy import select, delete
from uuid import UUID
from typing import List

from src.app.database.models import Enrollment
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