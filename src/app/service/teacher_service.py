from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database.db import AsyncSession
from src.app.database.models import User, Role, Course, Faculty
from src.app.security.security_context import hash_password
from src.app.api.schemas.user import TeacherCreate

#register new teacher
async def add_new_teacher(
        session: AsyncSession, 
        personel: TeacherCreate
):
    faculty = await session.get(Faculty, personel.faculty_id)

    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty with ID: {personel.faculty_id} not found."
        )
    
    role = await session.scalar(
        select(Role).where(Role.name == "TEACHER") 
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role not found"
        )
    
    new_user = User(
        **personel.model_dump(exclude={"password"}),
        password=hash_password(personel.password)
    )

    new_user.roles.append(role)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "Registered successfully."}


async def get_all_teacher(
        session: AsyncSession,
        teacher_id: UUID | None = None
):
    if not teacher_id:
        result = await session.execute(
            select(User)
            .join(User.roles)
            .where(Role.name == "TEACHER")
        ) 
        teachers = result.scalars().unique().all()

        return teachers
    
    elif teacher_id:
        result = await session.execute(
            select(User)
            .join(User.roles)
            .where(
                User.id == teacher_id,
                Role.name == "TEACHER"
            )
        )
        existing_teacher = result.scalar_one_or_none()

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher by this ID {teacher_id} not found."
            )
        
        return existing_teacher


async def delete_teacher_by_user_id(
        session: AsyncSession,
        teacher_id: UUID
):
    result = await session.execute(
        select(User)
        .where(User.id == teacher_id)       
    )
    existing_teacher = result.scalar_one_or_none()

    if not existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID: {teacher_id} not found."
        )
    
    await session.delete(existing_teacher)
    await session.commit()

    return {"detail": f"Teacher with ID: {teacher_id} deleted."}


async def teacher_courses_by_user_id(
        session: AsyncSession,
        teacher: User
):
    result = await session.execute(
        select(User)
        .join(User.roles)
        .where(
            User.id == teacher.id,
            Role.name == "TEACHER"
        )
        .options(selectinload(User.courses))
    )
    teacher = result.scalar_one_or_none()

    return teacher.courses


async def list_student_of_courses_by_course_id(
        session: AsyncSession,
        course_id: int,
        teacher: User
):
    existing_course = await session.get(Course, course_id)

    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID: {course_id} not found."
        )
    
    result = await session.execute(
        select(User.id)
        .where(
            User.id == teacher.id,
            User.courses.any(Course.id == course_id)
        )
    )
    teacher_exists = result.scalar_one_or_none()

    if not teacher_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher does not teach this course with ID {course_id}"
        )

    
    result = await session.execute(
        select(User)
        .join(User.roles)
        .where(
            Role.name == "STUDENT",
            User.courses.any(Course.id == course_id)
        ) 
    )
    students = result.scalars().unique().all()

    return students


    

    


