from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.security.security_context import hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User, Role, Faculty, Section
from src.app.api.schemas.user import StudentCreate, StudentCourse

#register new student
async def add_new_student(
        session: AsyncSession, 
        student: StudentCreate
):
    existing_faculty = await session.get(Faculty, student.faculty_id)

    if not existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty by this ID: {student.faculty_id} not found."
        )
    
    existing_section = await session.get(Section, student.section_id)

    if not existing_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section by this ID: {student.section_id} not found."
        )

    if existing_section.faculty_id != student.faculty_id:
        raise HTTPException(
            status_code=400,
            detail="Section does not belong to this faculty."
        )


    result = await session.execute(
        select(User).where(User.student_id == student.student_id)
    )

    existing_student = result.scalar_one_or_none()

    if existing_student: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this student ID already exists."
        ) 
    
    role = await session.scalar(
        select(Role).where(Role.name == "STUDENT") 
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role not found"
        )
    
    new_user = User(
        **student.model_dump(exclude={"password"}),
        password=hash_password(student.password)
    )

    new_user.roles.append(role)

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    except:
        await session.rollback()
        raise

    return {"message: ", "Student Registered successfully."}


async def get_student_by_info(
        session: AsyncSession,
        user: StudentCourse
):
    if user.student_id:
        result = await session.execute(
            select(User).where(
                User.student_id == user.student_id
            )
        )

        existing_student = result.scalar_one_or_none()

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with this Student ID not exists."
            )
        
        return existing_student
    
    elif user.name and user.surname:
        result = await session.execute(
            select(User).where(
                User.name == user.name,
                User.surname == user.surname
            )
        )

        existing_student= result.scalar_one_or_none()

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with this Student name and surname not exists."
            )
        
        return existing_student
    

async def get_all_student_by_section_and_faculty_id(
        session: AsyncSession,
        faculty_id: int,
        section_id: int
):
    existing_faculty = await session.get(Faculty, faculty_id)

    if not existing_faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty by this ID: {faculty_id} not found."
        )
    
    existing_section = await session.get(Section, section_id)

    if not existing_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section by this ID: {section_id} not found."
        )
    
    result = await session.execute(
        select(User).where(
            User.faculty_id == faculty_id,
            User.section_id == section_id
        )
    )

    students = result.scalars().all()

    return students  


async def delete_student_by_student_id(
        session: AsyncSession,
        student_id: str
):
    result = await session.execute(
        select(User).where(
            User.student_id == student_id
        )
    )

    existing_student = result.scalar_one_or_none()

    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student by student ID not found."
        )
    
    await session.delete(existing_student)
    await session.commit()

    return {"detail": "Student successfully deleted."}