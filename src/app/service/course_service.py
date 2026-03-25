from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
from uuid import UUID

import logging

from src.app.database.db import AsyncSession
from src.app.api.schemas.course import CourseCreate, CourseUpdate
from src.app.database.models import Course, Section, User, Role, Enrollment
from src.app.repositories.section_repository import SectionRepository
from src.app.repositories.course_repository import CourseRepository
from src.app.repositories.user_repository import UserRepository
from src.app.repositories.enrollment_repository import EnrollmentRepository

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
    

class CourseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.section_repo = SectionRepository(session=self.session)
        self.course_repo = CourseRepository(session=self.session)

    async def add_new_course(self, course: CourseCreate):
        try:
            existing_sections = await self.section_repo.find_with_ids(ids=course.section_ids)

            if len(course.section_ids) != len(existing_sections):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Some Sections not found."
                )

            existing_course = await self.course_repo.get_course_by_code(course_code=course.course_code)

            if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course already exists in sections."
                )
            
            new_course = Course(
                **course.model_dump(exclude={"section_ids"}),
            )

            new_course.sections = existing_sections

            self.session.add(new_course)
            await self.session.commit()
            await self.session.refresh(new_course)

            return {
                "message": "Courses successfully added.",
                "Course": new_course
            }

        except IntegrityError:
            await self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course already exists."
            )
        
    async def get_course_by_id(
            self,
            section_id: int,
            course_id: int | None = None
    ):
        existing_section = await self.section_repo.find_by_id(id=section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        if not course_id:
            courses = await self.course_repo.get_course_with_section_id(section_id=section_id)

            return courses

        elif course_id:
            existing_course = await self.course_repo.get_course_with_section_id(section_id=section_id, course_id=course_id)

            if not existing_course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Courses by this ID: {course_id} not found in this section."
                )
            
            return existing_course  

    async def get_course_by_course_code(self, course_code: str) -> Course:
        existing_course = await self.course_repo.get_course_by_code(course_code=course_code)

        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with code: {course_code} not found."
            )
        
        return existing_course
    
    async def delete_course_id(
            self,
            section_id: int,
            course_id: int
    ):
        existing_section = await self.section_repo.find_by_id(id=section_id)

        if not existing_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        existing_course = await self.course_repo.get_course_with_section_id(section_id=section_id, course_id=course_id)

        if not existing_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course by this ID: {course_id} not found in this section."
            )
        
        await self.session.delete(existing_course)
        await self.session.commit()

        return {"detail": "Course successfully deleted."}
    
    async def update_course_by_id(
            self,
            course_id: int,
            course_update: CourseUpdate
    ):
        try:   
            existing_course = await self.course_repo.find_by_id(id=course_id)

            if not existing_course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course by this ID: {course_id} not found."
                )
            course_data = course_update.model_dump(exclude={"section_ids"}, exclude_unset=True)
            
            for field, value in course_data.items():
                setattr(existing_course, field, value)
            
            if course_update.section_ids is not None:
                existing_sections = await self.section_repo.find_with_ids(ids=course_update.section_ids)

                if len(existing_sections) != len(course_update.section_ids):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Some sections not found."
                    )

                existing_course.sections = existing_sections

            await self.session.commit() 
            await self.session.refresh(existing_course)

            return {
                "message": "Courses successfully updated.",
                "Course": existing_course
            }
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error."
            )
    

class StudentCourseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session=self.session)
        self.section_repo = SectionRepository(session=self.session)
        self.user_repo = UserRepository(session=self.session)
        self.enrollment_repo = EnrollmentRepository(session=self.session)

    async def get_course_for_student(
            self,
            student: User
    ) -> List[dict]:  
        semester = current_semester()  

        if semester is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Course selection is closed."
            )
        
        courses = await self.course_repo.get_course_with_class_and_semester(student_class=student.class_, semester=semester)

        return courses
    

    async def get_failed_courses_of_student(
            self, 
            student: User,
    ):
        failed_courses = await self.course_repo.failed_courses_of_student(student_id=student.id)

        return failed_courses
    
    async def select_course_with_course_id(
            self,
            selected_course_id: int,
            student: User
    ):
        semester = current_semester()
        max_option = optional_course_max_select(student_class=student.class_, semester=semester)

        course = await self.course_repo.get_course_with_id_and_semester(
            course_id=selected_course_id, 
            semester=semester, 
        )

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found in this semester."
            )
        
        student_course = await self.user_repo.check_student_course_with_course_id(
            course_id=selected_course_id, 
            student_id=student.id
        )

        if student_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already have this course."
            )
        
        new_enrollment = Enrollment(
            course_id = selected_course_id,
            student_id = student.id
        )

        self.session.add(new_enrollment)
        self.session.commit()
        self.session.refresh(new_enrollment)

        return {"detail": "Course successfully selected."}


    async def course_selection_for_student(
            self,
            student_selected_course_ids: List[int],
            student: User,
    ):
        selected_course_ids = list(set(student_selected_course_ids))
        semester = current_semester()  

        if semester is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Course selection is closed."
            )
        
        current_student = await self.user_repo.get_student_with_courses(student_id=student.student_id)
        
        student_max_option = await optional_course_max_select(student_class=current_student.class_, semester=semester)

        if len(selected_course_ids) > student_max_option:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You can select only {student_max_option} optional courses."
            )
        
        courses = await self.course_repo.get_course_with_class_and_semester(student_class=student.class_, semester=semester)

        compulsory_courses = [c for c in courses if not c.is_optional]
        optional_courses = [c for c in courses if c.is_optional]

        existing_ids = {c.course_id for c in current_student.enrollments}
        
        courses_to_add = []
        
        for course in compulsory_courses:
            if course.id not in existing_ids:
                new_enrollment = Enrollment(
                    course_id = course.id,
                    student_id = current_student.id
                )
                courses_to_add.append(new_enrollment)
                existing_ids.add(course.id)
        
        optional_map = {c.id: c for c in optional_courses}

        for course_id in selected_course_ids:
                if course_id not in optional_map:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid optional course."
                    )

                if course_id not in existing_ids:
                    new_enrollment = Enrollment(
                        course_id = course_id,
                        student_id = current_student.id
                    )
                    courses_to_add.append(new_enrollment)
                    existing_ids.add(course.id)
        
        self.session.add_all(courses_to_add)
        await self.session.commit()
        
        course_info = [
            {"id": e.course_id, "name": optional_map.get(e.course_id, {c.id: c for c in compulsory_courses}[e.course_id]).name}
            if e.course_id in optional_map else
            {"id": e.course_id, "name": {c.id: c for c in compulsory_courses}[e.course_id].name}
            for e in courses_to_add
        ]
        
        return {
            "message": "Courses successfully selected.",
            "courses": course_info
        } 

    
    async def custom_course_add_for_student(
            self,
            student_id: str,
            course_ids: List[int]
    ):
        student = await self.user_repo.get_student_with_courses(student_id=student_id)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student by student ID: {student_id} not found."
            )
        
        semester = current_semester()
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Course selection is closed."
            )
    
        courses = await self.course_repo.get_courses_with_ids_and_semester(course_ids=course_ids, semester=semester)

        found_ids = {c.id for c in courses}
        missing_ids = set(course_ids) - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courses not found: {list(missing_ids)}"
            )
                
        students_existing_course = {c.course_id for c in student.enrollments}

        courses_to_add = [
            course for course in courses
            if course.id not in students_existing_course
        ]

        if not courses_to_add:
            return {"detail": "No new courses to add"}

        courses_to_add_objs = [
            Enrollment(course_id=c.id, student_id=student.id)
            for c in courses_to_add
        ]

        self.session.add_all(courses_to_add_objs)

        await self.session.commit()

        return {
            "detail": "Courses successfully added to student",
            "added_courses": [{"id": c.id, "name": c.name} for c in courses_to_add]
        }
    
    async def get_courses_that_student_can(
            self,
            student: User
    ):
        user = await self.user_repo.get_student_with_courses(student_id=student.student_id)

        return user.enrollments
       
    async def delete_student_courses_by_id(
            self,
            section_id: int,
            student_id: UUID | None = None, 
            course_id: int | None = None
    ):
        section = await self.section_repo.find_by_id(id=section_id)

        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        if student_id is None:
            students = await self.user_repo.get_student_with_section_id(section_id=section_id)
            student_ids = [s.id for s in students]
            
            if not student_ids:
                return {"detail": "No students found in this sections."}
            
            deleted_course_of_students = await self.enrollment_repo.delete_course_of_students(student_ids=student_ids)

            if not deleted_course_of_students:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Some courses of students not deleted."
                )
            
            await self.session.commit()

            return {"detail": f"Courses of students in this section ID: {section_id} deleted."}
        
        existing_student = await self.user_repo.get_user(user_id=student_id)

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student not found with ID: {student_id} not found."
            )
        
        if course_id is not None:
            deleted_ids = await self.enrollment_repo.delete_with_student_id_and_course_id(student_id=student_id, course_id=course_id)
            
            if not deleted_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course {course_id} not found for this student."
                )
            
            await self.session.commit()

            return {"detail": f"Course with ID: {course_id} removed from student."}
        
        deleted_course_of_student = await self.enrollment_repo.delete_with_student_id(student_id=student_id)

        if not deleted_course_of_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Courses of student not deleted or not found."
            )
        
        await self.session.commit()

        return {"detail": f"All courses of student with ID {student_id} deleted."}
    
    async def get_student_and_courses_by_student_id(
            self,
            student_id: str
    ):
        existing_student = await self.user_repo.get_student_with_courses(student_id=student_id)

        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student by this student ID : {student_id} not found."
            )
        
        return existing_student.enrollments
    
    async def numbers_of_student_of_current_course(
            self,
            course_id: int,
    ):
        student_count = await self.user_repo.count_student_in_course(course_id=course_id)

        return student_count
    
class TeacherCourseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)
        self.section_repo = SectionRepository(session=self.session)
        self.course_repo = CourseRepository(session=self.session)
    
    async def add_course_for_teacher_by_teacher_id(
            self,
            teacher_id: UUID,
            course_ids: List[int]
    ):
        existing_teacher = await self.user_repo.get_teacher_with_courses(teacher_id=teacher_id)

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher by this ID {teacher_id} not found."
            )
        semester = current_semester()

        if semester is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Course selection is closed."
            )

        courses = await self.course_repo.get_courses_with_ids_and_semester(course_ids=course_ids, semester=semester)

        found_ids = {c.id for c in courses}
        missing_ids = set(course_ids) - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courses not found: {list(missing_ids)}"
            )
        
        teachers_existing_course = {c.id for c in existing_teacher.teaching_courses}

        courses_to_add = [
            c for c in courses
            if c.id not in teachers_existing_course
        ]

        if not courses_to_add:
            return {"detail": "No new courses to add"}

        existing_teacher.teaching_courses.extend(courses_to_add)

        await self.session.commit()

        return {
            "detail": "Courses successfully added to teacher",
            "added_courses": [{"id": c.id, "name": c.name} for c in courses_to_add]
        }
    
    async def get_courses_of_teacher_by_id(
            self,
            teacher_id: UUID
    ):
        existing_teacher = await self.user_repo.get_teacher_with_courses(teacher_id=teacher_id)

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher by this ID {teacher_id} not found."
            )
        
        return existing_teacher
    
    async def delete_courses_of_teacher_by_id(
            self,
            section_id: int,
            course_id: int | None = None,
            teacher_id: UUID | None = None
    ):
        section = await self.section_repo.find_by_id(id=section_id)

        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section by this ID: {section_id} not found."
            )
        
        if teacher_id is None:
            teachers = await self.user_repo.get_teachers_with_courses_in_section(section_id=section_id)
    
            for teacher in teachers:
                teacher.teaching_courses.clear()

            await self.session.commit()
            
            return {"detail": f"Courses of teachers in this section ID: {section_id} deleted."}
        
        existing_teacher = await self.user_repo.get_teacher_with_courses(teacher_id=teacher_id)

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher with ID: {teacher_id} not found."
            )
            
        if course_id is not None:
            course_to_remove = next(
                (c for c in existing_teacher.teaching_courses if c.id == course_id),
                None
            )

            if not course_to_remove:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course {course_id} not found for this teacher."
            )

            existing_teacher.teaching_courses.remove(course_to_remove) 

            await self.session.commit()

            return {"detail": f"Course with ID: {course_id} removed from teacher."}
        
        if not existing_teacher.teaching_courses:
            return {"detail": "Teacher has no courses."}
        
        existing_teacher.teaching_courses.clear()

        await self.session.commit()

        return {"detail": f"All courses of teacher with ID {teacher_id} deleted."}