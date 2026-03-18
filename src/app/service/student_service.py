from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.security.security_context import hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User, Role, Faculty, Section
from src.app.api.schemas.user import StudentCreate, StudentCourse
from src.app.repositories.user_repository import UserRepository


class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)

    #register new student
    async def add_new_student(
            self, 
            student: StudentCreate
    ):
        existing_faculty = await self.session.get(Faculty, student.faculty_id)

        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {student.faculty_id} not found."
            )
        
        existing_section = await self.session.get(Section, student.section_id)

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


        result = await self.session.execute(
            select(User).where(User.student_id == student.student_id)
        )

        existing_student = result.scalar_one_or_none()

        if existing_student: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A student with this student ID already exists."
            ) 
        
        role = await self.session.scalar(
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
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
        except:
            await self.session.rollback()
            raise

        return {"message: ", "Student Registered successfully."}

    async def get_all_students(self):
        result = await self.session.execute(
            select(User)
            .join(User.roles)
            .where(Role.name == "STUDENT")
        )
        students = result.scalars().all()

        return students

    async def get_student_by_info(
            self,
            user: StudentCourse
    ):
        if user.student_id:
            result = await self.session.execute(
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
            result = await self.session.execute(
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
            self,
            faculty_id: int,
            section_id: int
    ):
        existing_faculty = await self.session.get(Faculty, faculty_id)

        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {faculty_id} not found."
            )
        
        existing_section = await self.session.get(Section, section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        result = await self.session.execute(
            select(User).where(
                User.faculty_id == faculty_id,
                User.section_id == section_id
            )
        )

        students = result.scalars().all()

        return students  


    async def delete_student_by_student_id(
            self,
            student_id: str
    ):
        result = await self.session.execute(
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
        
        await self.session.delete(existing_student)
        await self.session.commit()

        return {"detail": "Student successfully deleted."}
    
    async def get_student_profile(self, user: User):
        existing_student = await self.user_repo.get_student_profile(user_id=user.id)

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found."
            )
        
        return existing_student