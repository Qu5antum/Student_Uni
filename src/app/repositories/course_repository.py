from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from src.app.database.models import Course, Section
from .base_repository import BaseRepository


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