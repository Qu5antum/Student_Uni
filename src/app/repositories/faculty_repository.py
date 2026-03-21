from sqlalchemy import select

from .base_repository import BaseRepository
from src.app.database.models import Faculty


class FacultyRepository(BaseRepository):
    model = Faculty

    async def get_by_faculty_name(self, name: str):
        result = await self.session.execute(
            select(self.model).where(self.model.name == name)
        )

        return result.scalar_one_or_none()