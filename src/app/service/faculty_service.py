from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.database.db import AsyncSession
from src.app.database.models import Faculty
from src.app.api.schemas.faculty import FacultyCreate


async def add_new_faculty(session: AsyncSession, faculty: FacultyCreate):
    result = await session.execute(
        select(Faculty).where(Faculty.name == faculty.name)
    )

    existing_faculty = result.scalar_one_or_none()

    if existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Faculty already exists."
        )
    
    new_faculty = Faculty(
        **faculty.model_dump()
    )   

    session.add(new_faculty)
    await session.commit()
    await session.refresh(new_faculty)

    return new_faculty


async def delete_faculty_by_id(
        session: AsyncSession,
        faculty_id: int
):
    existing_faculty = await session.get(Faculty, faculty_id)
    
    if not existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty by this id: {faculty_id} not found."
        )
    
    await session.delete(existing_faculty)
    await session.commit()

    return {"detail": "Faculty successfully deleted."}
