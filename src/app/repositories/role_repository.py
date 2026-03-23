from uuid import UUID
from sqlalchemy import select

from .base_repository import BaseRepository
from src.app.database.models import Role, User


class RoleRepository(BaseRepository):
    model = Role

    async def get_teacher_role(self):
        result = await self.session.execute(
            select(self.model).where(self.model.name == "TEACHER")
        )

        return result.scalar_one_or_none()
    
    async def get_student_role(self):
        result = await self.session.execute(
            select(self.model).where(self.model.name == "STUDENT")
        )

        return result.scalar_one_or_none()
    
