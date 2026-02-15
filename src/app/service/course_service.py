from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

import logging

from src.app.database.db import AsyncSession
from src.app.api.schemas.course import CourseCreate
from src.app.database.models import Course, Section, User

logger = logging.getLogger(__name__)

def current_semester():
    month = datetime.now().month
    if 9 <= month <= 12 : return "Autumn"
    elif 1 <= month <= 7: return "Spring"
    else: return None

async def optional_course_max_select(student_class: int, semester: str) -> int:
    if semester is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Course selection is closed."
        )
    
    if student_class == 2 and semester == "Spring":
        return 1
    elif student_class == 4 and semester == "Spring":
        return 1
    else:
        return 3
    

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
                Course.section_id == course.section_id,
                Course.course_code == course.course_code
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


async def get_course_for_student(
        session: AsyncSession,
        student: User
) -> List[dict]:  
    semester = current_semester()  

    if semester is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Course selection is closed."
        )
    
    result_course = await session.execute(
        select(Course).where(
            Course.course_class == student.class_,
            Course.course_semester == semester
        )
    )
    courses = result_course.scalars().all()

    return courses


async def course_selection_for_student(
        session: AsyncSession,
        student_selected_course_ids: List[int],
        student: User,
):
    # Надо добавить проверку на верность того что студент именно выберает те курсы которые он может выбирвать по семестру и его классу
    selected_course_ids = list(set(student_selected_course_ids))
    semester = current_semester()  

    if semester is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Course selection is closed."
        )
    
    result = await session.execute(
        select(User)
        .where(User.id == student.id)
        .options(selectinload(User.courses))
    )
    current_student = result.scalar_one_or_none()
    
    student_max_option = await optional_course_max_select(student_class=current_student.class_, semester=semester)

    if len(selected_course_ids) > student_max_option:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can select only {student_max_option} optional courses."
        )
        
    result_course = await session.execute(
        select(Course).where(
            Course.course_class == current_student.class_,
            Course.course_semester == semester
        )
    )
    courses = result_course.scalars().all()

    compulsory_courses = [c for c in courses if c.is_optional]
    optional_courses = [c for c in courses if not c.is_optional]

    existing_ids = {c.id for c in current_student.courses}

    logger.info("Compulsary courses: %s", [c.id for c in compulsory_courses])

    for course in compulsory_courses:
        if course.id not in existing_ids:
            current_student.courses.append(course)
            existing_ids.add(course.id)

    optional_map = {c.id: c for c in optional_courses}

    for course_id in selected_course_ids:
            if course_id not in optional_map:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid optional course."
                )

            if course_id not in existing_ids:
                current_student.courses.append(optional_map[course_id])
                existing_ids.add(course_id)
    
    await session.flush()
    await session.commit()

    return {
        "message": "Courses successfully selected.",
        "courses": [{"id": c.id, "name": c.name} for c in current_student.courses]
    }


async def get_student_courses_(
        session: AsyncSession,
        student: User
):
    result = await session.execute(
        select(User)
        .where(User.id == student.id)
        .options(selectinload(User.courses))
    )

    user = result.scalar_one_or_none()

    return user.courses

    

    







    
    
    


