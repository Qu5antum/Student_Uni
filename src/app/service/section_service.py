from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.app.database.db import AsyncSession
from src.app.database.models import Section, Faculty
from src.app.api.schemas.section import SectionCreate


class SectionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add_new_section(
            self,
            section: SectionCreate
    ):
        try:
            existing_faculty = await self.session.get(Faculty, section.faculty_id)

            if not existing_faculty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Faculty not found."
                )
            
            result = await self.session.execute(
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

            self.session.add(new_section)
            await self.session.commit()
            await self.session.refresh(new_section)

            return new_section
        except IntegrityError:
            await self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section already exists."
            )
        

    async def get_section_by_id(
            self,
            faculty_id: int,
            section_id: int | None = None
    ):
        existing_faculty = await self.session.get(Faculty, faculty_id)
        
        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {faculty_id} not found."
            )
        
        if not section_id:
            result = await self.session.execute(
                select(Section).where(Section.faculty_id == faculty_id)
            )

            sections = result.scalars().all()
        
            return sections
        
        elif section_id:
            result = await self.session.execute(
                select(Section).where(
                    Section.id == section_id,
                    Section.faculty_id == faculty_id
                )
            )

            existing_section = result.scalar_one_or_none()

            if not existing_section:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section by this ID: {section_id} not found in this faculty."
                )
            
            return existing_section
        

    async def delete_section_by_id(
            self,
            faculty_id: int,
            section_id: int | None = None
    ):
        existing_faculty = await self.session.get(Faculty, faculty_id)
        
        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {faculty_id} not found."
            )
        
        result = await self.session.execute(
            select(Section).where(
                Section.id == section_id,
                Section.faculty_id == faculty_id
            )
        )

        existing_section = result.scalar_one_or_none()

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found in this faculty."
            )
        
        await self.session.delete(existing_section)
        await self.session.commit()

        return {"detail": "Section successfully deleted."}
            

            




    

    