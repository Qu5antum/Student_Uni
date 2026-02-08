from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.database.db import AsyncSession
from src.app.database.models import Section
from src.app.api.schemas.section import SectionCreate


async def add_new_section(
        session: AsyncSession,
        section: SectionCreate
):
    section = await session