from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database.db import AsyncSession
from src.app.database.models import User, Role, Course, Faculty
from src.app.security.security_context import hash_password
from src.app.api.schemas.user import TeacherCreate
from src.app.api.schemas.enrollment import ExamType
from src.app.repositories.user_repository import UserRepository
from src.app.repositories.role_repository import RoleRepository
from src.app.repositories.faculty_repository import FacultyRepository
from src.app.repositories.course_repository import CourseRepository
from src.app.repositories.enrollment_repository import EnrollmentRepository


class TeacherService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)
        self.role_repo = RoleRepository(session=self.session)
        self.faculty_repo = FacultyRepository(session=self.session)
        self.course_repo = CourseRepository(session=self.session)
        self.enrollment_repo = EnrollmentRepository(session=self.session)

    #register new teacher
    async def add_new_teacher(
            self, 
            personel: TeacherCreate
    ):
        faculty = await self.faculty_repo.find_by_id(id=personel.faculty_id)

        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Faculty with ID: {personel.faculty_id} not found."
            )
        
        role = await self.role_repo.get_teacher_role()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role not found."
            )
        
        new_user = User(
            **personel.model_dump(exclude={"password"}),
            password=hash_password(personel.password)
        )

        new_user.roles.append(role)

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return {"message": "Registered successfully."}


    async def get_all_teacher(
            self,
            teacher_id: UUID | None = None
    ):
        if not teacher_id: 
            teachers = await self.user_repo.get_teachers()

            return teachers
        
        elif teacher_id:
            existing_teacher = await self.user_repo.get_teacher_with_courses(teacher_id=teacher_id)

            if not existing_teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Teacher by this ID {teacher_id} not found."
                )
            
            return existing_teacher


    async def delete_teacher_by_user_id(
            self,
            teacher_id: UUID
    ):
        existing_teacher = await self.user_repo.get_teacher(teacher_id=teacher_id)

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with ID: {teacher_id} not found."
            )
        
        await self.session.delete(existing_teacher)
        await self.session.commit()

        return {"detail": f"Teacher with ID: {teacher_id} deleted."}


    async def teacher_courses_by_user_id(
            self,
            teacher: User
    ):
        teacher = await self.user_repo.get_teacher_with_courses(teacher_id=teacher.id)

        return teacher.teaching_courses


    async def list_student_of_courses_by_course_id(
            self,
            course_id: int,
            teacher: User
    ):
        teacher_exists = await self.user_repo.get_teacher(teacher_id=teacher.id, course_id=course_id)

        if not teacher_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher does not teach this course with ID {course_id}"
            )

        students = await self.user_repo.get_students(course_id=course_id)

        return students
    
    async def get_teacher_profile(self, user: User):
        existing_teacher = await self.user_repo.get_teacher_profile(user_id=user.id)

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found."
            )
        
        return existing_teacher
    
    async def add_grade_for_student(
            self,
            grade: float,
            course_id: int,
            student_id: str,
            exam_type: ExamType,
            teacher: User
    ):
        teacher_course = await self.user_repo.check_teacher_course(teacher_id=teacher.id, course_id=course_id)

        if not teacher_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This course not belong to the teacher."
            )
        
        student_enrollment = await self.enrollment_repo.get_enrollment_with_student_id_course_id(course_id=course_id, student_id=student_id)

        if not student_enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment not found for student {student_id} and course {course_id}."
            )

        if exam_type == ExamType.MIDTERM:
            student_enrollment.midterm_grade = grade
        elif exam_type == ExamType.FINAL:
            student_enrollment.final_grade = grade
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="exam_type must be either (midterm) or (final)."
            )
        
        self.enrollment_repo.session.add(student_enrollment)
        await self.session.commit()
        await self.session.refresh(student_enrollment)
        
        return student_enrollment.midterm_grade
    
    async def get_student_grades(
            self,
            teacher: User,
            course_id: int,
            student_id: str | None = None,
    ):
        teacher_course = await self.user_repo.check_teacher_course(teacher_id=teacher.id, course_id=course_id)

        if not teacher_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This course not belong to the teacher."
            )
        if not student_id: 
            student_enrollment = await self.enrollment_repo.get_enrollment_with_student_id_course_id(course_id=course_id)
        elif student_id:
            student_enrollment = await self.enrollment_repo.get_enrollment_with_student_id_course_id(course_id=course_id, student_id=student_id)

        if not student_enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment not found for student {student_id} and course {course_id}."
            )
        
        return student_enrollment
        
        


        