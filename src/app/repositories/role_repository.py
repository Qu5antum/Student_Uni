from uuid import UUID
from sqlalchemy import select

from .base_repository import BaseRepository
from src.app.database.models import Role, User


class RoleRepository(BaseRepository):
    model = Role
    
    async def get_user_role(self, user_id: UUID):
        result = await self.session.execute(
            select(Role.name)
            .join(Role.users)
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()