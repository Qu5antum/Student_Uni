from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.app.database.db import AsyncSession
from src.app.api.schemas.course import CourseCreate
from src.app.database.models import Course, Section


async def add_new_course(
        session: AsyncSession,
        course: CourseCreate
):
    try:
        existing_section = await session.get(Section, course.section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found."
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


