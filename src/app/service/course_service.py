from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

import logging

from src.app.database.db import AsyncSession
from src.app.api.schemas.course import CourseCreate, CourseUpdate
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

        return {
            "message": "Courses successfully added.",
            "Course": new_course
        }

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

    compulsory_courses = [c for c in courses if not c.is_optional]
    optional_courses = [c for c in courses if c.is_optional]

    existing_ids = {c.id for c in current_student.courses}


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

async def custom_course_add_for_student(
        session: AsyncSession,
        student_id: str,
        course_ids: List[int]
):
    result = await session.execute(
        select(User)
        .where(User.student_id == student_id)
        .options(selectinload(User.courses))
    )
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student by student ID: {student_id} not found."
        )
    
    result = await session.execute(
        select(Course).where(
            Course.id.in_(course_ids),
            Course.course_semester == current_semester()
        )
    )
    courses = result.scalars().all()

    found_ids = {c.id for c in courses}
    missing_ids = set(course_ids) - found_ids

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Courses not found or wrong semester: {list(missing_ids)}"
        )
            
    students_existing_course = {c.id for c in student.courses}

    courses_to_add = [
        course for course in courses
        if course.id not in students_existing_course
    ]

    student.courses.extend(courses_to_add)

    await session.commit()

    return {
        "detail": "Courses successfully added to student",
        "added_courses": [{"id": c.id, "name": c.name} for c in courses_to_add]
    }


async def get_courses_that_student_can(
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


async def update_course_by_id(
        session: AsyncSession,
        course_id: int,
        course_update: CourseUpdate
):
    existing_course = await session.get(Course, course_id)

    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course by this ID: {course_id} not found."
        )
    course_data = course_update.model_dump(exclude_unset=True)

    if "section_id" in course_data:
        existing_section = await session.get(Section, course_data["section_id"])

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {course_data['section_id']} not found."
            )
    
    for field, value in course_data.items():
        setattr(existing_course, field, value)

    await session.commit() 
    await session.refresh(existing_course)

    return {
        "message": "Courses successfully updated.",
        "Course": existing_course
    }


async def delete_student_courses_by_id(
        session: AsyncSession,
        section_id: int | None = None,
        student_id: str | None = None
):
    if not student_id and not section_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide student_id or section_id"
        )

    if student_id:
        result = await session.execute(
            select(User)
            .where(User.student_id == student_id)
            .options(selectinload(User.courses))
        )
        existing_student = result.scalar_one_or_none()

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student by this student ID: {student_id} nof found."
            )
        
        existing_student.courses.clear()
        await session.commit()

        return {"detail": f"Courses of student by student ID: {student_id} deleted."}
    
    if section_id:
        section = await session.get(Section, section_id)

        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        result = await session.execute(
            select(User)
            .where(User.section_id == section_id)
            .options(selectinload(User.courses))
        )
        students = result.scalars().all()
   
        for student in students:
            student.courses.clear()

        await session.commit()

        return {"detail": f"Courses of students in this section ID: {section_id} deleted."}
    

async def get_student_and_courses_by_student_id(
        session: AsyncSession,
        student_id: str
):
    result = await session.execute(
        select(User)
        .where(User.student_id == student_id)
        .options(selectinload(User.courses))
    )
    existing_student = result.scalar_one_or_none()

    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student by this student ID : {student_id} not found."
        )
    
    return existing_student
    