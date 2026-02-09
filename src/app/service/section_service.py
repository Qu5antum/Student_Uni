from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.database.db import AsyncSession
from src.app.database.models import Section
from src.app.api.schemas.section import SectionCreate


async def add_new_section(
        session: AsyncSession,
        section: SectionCreate
):
    existing_section = await session.execute(
        select(Section).where(
            Section.name == section.name,
            Section.faculty_id == section.faculty_id
        )
    )

    if existing_section:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section already exists and faculty ID is wrong."
        )
    
    new_section = Section()
    

    