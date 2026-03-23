from fastapi import HTTPException, status
from sqlalchemy import select

from src.app.security.security_context import hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User, Role, Faculty, Section
from src.app.api.schemas.user import StudentCreate, StudentCourse
from src.app.repositories.user_repository import UserRepository
from src.app.repositories.faculty_repository import FacultyRepository
from src.app.repositories.section_repository import SectionRepository
from src.app.repositories.role_repository import RoleRepository


class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)
        self.faculty_repo = FacultyRepository(session=self.session)
        self.section_repo = SectionRepository(session=self.session)
        self.role_repo = RoleRepository(session=self.session)

    #register new student
    async def add_new_student(
            self, 
            student: StudentCreate
    ):
        existing_faculty = await self.faculty_repo.find_by_id(id=student.faculty_id)

        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {student.faculty_id} not found."
            )
        
        existing_section = await self.section_repo.find_by_id(id=student.section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {student.section_id} not found."
            )

        if existing_section.faculty_id != student.faculty_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section does not belong to this faculty."
            )

        existing_student = await self.user_repo.get_student_with_student_id(student_id=student.student_id)

        if existing_student: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A student with this student ID already exists."
            ) 
        
        role = await self.role_repo.get_student_role()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role not found."
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

        return {"message": "Student Registered successfully."}

    async def get_all_students(self):
        students = await self.user_repo.get_students()

        return students

    async def get_student_by_info(
            self,
            user: StudentCourse
    ):
        if user.student_id:
            existing_student = await self.user_repo.get_student_with_student_id(student_id=user.student_id)

            if not existing_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student with this Student ID not exists."
                )
            
            return existing_student
        
        elif user.name and user.surname:
            existing_student= await self.user_repo.get_students(name=user.name, surname=user.surname)

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
        existing_faculty = await self.faculty_repo.find_by_id(id=faculty_id)

        if not existing_faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty by this ID: {faculty_id} not found."
            )
        
        existing_section = await self.user_repo.find_by_id(id=section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        if existing_section.faculty_id != faculty_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section does not belong to this faculty."
            )

        students = await self.user_repo.get_students(faculty_id=faculty_id, section_id=section_id)

        return students  


    async def delete_student_by_student_id(
            self,
            student_id: str
    ):
        existing_student = await self.user_repo.get_student_with_student_id(student_id=student_id)

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student with this student ID not found."
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