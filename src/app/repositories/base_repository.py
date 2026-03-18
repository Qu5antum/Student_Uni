from abc import ABC, abstractmethod

from src.app.database.db import AsyncSession

class AbstractRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: int):
        raise NotImplementedError
    

class BaseRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: int):
        obj = await self.session.get(self.model, id)

        return obj