from abc import ABC, abstractmethod
from sqlalchemy import select

from src.app.database.db import AsyncSession

class AbstractRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def get_obj_by_id(self, id: int):
        raise NotImplementedError
    
    @abstractmethod
    async def return_model(self):
        raise NotImplementedError
    

class BaseRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: int):
        obj = await self.session.get(self.model, id)

        return obj
    
    async def get_obj_by_id(self, id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )

        return result.scalar_one_or_none()
    
    async def return_model(self):
        result = await self.session.execute(
            select(self.model)
        )

        return result.scalars().all()

    