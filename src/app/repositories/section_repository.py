from sqlalchemy import select

from .base_repository import BaseRepository
from src.app.database.models import Section


class SectionRepository(BaseRepository):
    model = Section

    async def get_by_name_id(self, name: str, faculty_id: int):
        result = await self.session.execute(
            select(self.model).where(
                self.model.name == name,
                self.model.faculty_id == faculty_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_section_by_id_and_faculty_id(self, section_id: int, faculty_id: int):
        result = await self.session.execute(
                select(self.model).where(
                    self.model.id == section_id,
                    self.model.faculty_id == faculty_id
                )
            )
        
        return result.scalar_one_or_none()