from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.database.db import AsyncSession
from src.app.database.models import Faculty
from src.app.api.schemas.faculty import FacultyCreate
from src.app.repositories.faculty_repository import FacultyRepository


class FacultyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.faculty_repo = FacultyRepository(session=self.session)

    async def add_new_faculty(self, faculty: FacultyCreate):
        existing_faculty = await self.faculty_repo.get_by_faculty_name(name=faculty.name)

        if existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Faculty already exists."
            )
        
        new_faculty = Faculty(
            **faculty.model_dump()
        )   

        self.session.add(new_faculty)
        await self.session.commit()
        await self.session.refresh(new_faculty)

        return new_faculty


    async def get_faculy_by_id(
            self,
            faculty_id: int | None = None
    ):
        if not faculty_id:
            all_facultys = await self.faculty_repo.return_model()

            return all_facultys
        
        elif faculty_id:
            existing_faculty = await self.faculty_repo.get_obj_by_id(id=faculty_id)

            if not existing_faculty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Faculty by this ID: {faculty_id} not found."
                )
            
            return existing_faculty


    async def delete_faculty_by_id(
            self,
            faculty_id: int
    ):
        existing_faculty = await self.faculty_repo.find_by_id(id=faculty_id)
        
        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {faculty_id} not found."
            )
        
        await self.session.delete(existing_faculty)
        await self.session.commit()

        return {"detail": "Faculty successfully deleted."}
