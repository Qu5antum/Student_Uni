from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.app.database.db import AsyncSession
from src.app.database.models import Section, Faculty
from src.app.api.schemas.section import SectionCreate


async def add_new_section(
        session: AsyncSession,
        section: SectionCreate
):
    try:
        existing_faculty = await session.get(Faculty, section.faculty_id)

        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty not found."
            )
        
        result = await session.execute(
            select(Section).where(
                Section.name == section.name,
                Section.faculty_id == section.faculty_id
            )
        )

        existing_section = result.scalar_one_or_none()

        if existing_section:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section already exists in this faculty."
            )
        
        new_section = Section(
            **section.model_dump()
        )

        session.add(new_section)
        await session.commit()
        await session.refresh(new_section)

        return new_section
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section already exists."
        )
    

async def get_section_by_id(
        session: AsyncSession,
        faculty_id: int,
        section_id: int | None = None
):
    existing_faculty = await session.get(Faculty, faculty_id)
    
    if not existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty by this id: {faculty_id} not found."
        )
    
    if not section_id:
        result = await session.execute(
            select(Section).where(Section.faculty_id == faculty_id)
        )

        sections = result.scalars().all()
    
        return sections
    
    elif section_id:
        result = await session.execute(
            select(Section).where(
                Section.id == section_id,
                Section.faculty_id == faculty_id
            )
        )

        existing_section = result.scalar_one_or_none()

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this id: {section_id} not found in this faculty."
            )
        
        return existing_section
    

async def delete_section_by_id(
        session: AsyncSession,
        faculty_id: int,
        section_id: int | None = None
):
    existing_faculty = await session.get(Faculty, faculty_id)
    
    if not existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty by this id: {faculty_id} not found."
        )
    
    result = await session.execute(
        select(Section).where(
            Section.id == section_id,
            Section.faculty_id == faculty_id
        )
    )

    existing_section = result.scalar_one_or_none()

    if not existing_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section by this id: {section_id} not found in this faculty."
        )
    
    await session.delete(existing_section)
    await session.commit()

    return {"detail": "Section successfully deleted."}
        

        




    

    