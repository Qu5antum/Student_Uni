from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List

from src.app.database.db import AsyncSession
from src.app.api.schemas.course import CourseCreate
from src.app.database.models import Course, Section, User


async def add_new_course(
        session: AsyncSession,
        course: CourseCreate
):
    try:
        existing_section = await session.get(Section, course.section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {course.section_id} not found."
            )
        
        result = await session.execute(
            select(Course).where(
                Course.name == course.name,
                Course.section_id == course.section_id
            )
        )

        existing_course = result.scalar_one_or_none()

        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course already exists in this section."
            )
        
        new_course = Course(
            **course.model_dump()
        )

        session.add(new_course)
        await session.commit()
        await session.refresh(new_course)

        return new_course
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already exists."
        )


async def get_course_by_id(
        session: AsyncSession,
        section_id: int,
        course_id: int | None = None
):
    existing_section = await session.get(Section, section_id)

    if not existing_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section by this ID: {section_id} not found."
        )
    
    if not course_id:
        result = await session.execute(
            select(Course).where(
                Course.section_id == section_id
            )
        )

        course = result.scalars().all()

        return course

    elif course_id:
        result = await session.execute(
            select(Course).where(
                Course.id == course_id,
                Course.section_id == section_id
            )
        )
    
        existing_course = result.scalars().all()

        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courses by this ID: {course_id} not found in this section."
            )
        
        return existing_course
    

async def delete_course_id(
        session: AsyncSession,
        section_id: int,
        course_id: int
):
    existing_section = await session.get(Section, section_id)

    if not existing_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section by this ID: {section_id} not found."
        )
    
    result = await session.execute(
        select(Course).where(
            Course.id == course_id,
            Course.section_id == section_id
        )
    )

    existing_course = result.scalar_one_or_none()

    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course by this ID: {course_id} not found in this section."
        )
    
    await session.delete(existing_course)
    await session.commit()

    return {"detail": "Course successfully deleted."}


    
    


