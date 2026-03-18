from fastapi import APIRouter, status, Depends
from typing import List

from src.app.database.db import AsyncSession, get_session
from src.app.api.dependencies.check_role import require_roles
from src.app.api.dependencies.dependency import get_current_user
from src.app.api.schemas.user import StudentCourse, StudentCreate, StudentOut
from src.app.api.schemas.course import StudentCoursesOut
from src.app.database.models import User
from src.app.service.student_service import StudentService
from src.app.service.course_service import CourseService

student_route = APIRouter(
    prefix="/api/user/student",
    tags=["students"]
)


@student_route.post("/admin/register_student", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_student(
    user: StudentCreate,
    session: AsyncSession = Depends(get_session)
):
    student_service = StudentService(session=session)
    return await student_service.add_new_student(student=user)


@student_route.post(
        "/info", 
        response_model=StudentOut, 
        dependencies=[Depends(require_roles(["TECHER", "STUDENT", "ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_student_info(
    student: StudentCourse,
    session: AsyncSession = Depends(get_session)
):
    student_service = StudentService(session=session)
    return await student_service.get_student_by_info(user=student)

@student_route.get("/admin", response_model=List[StudentOut], dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_students(
    session: AsyncSession = Depends(get_session)
):
    student_service = StudentService(session=session)
    return await student_service.get_all_students()


@student_route.get(
        "/admin/faculties/{faculty_id}/sections/{section_id}/students", 
        response_model=List[StudentOut], 
        dependencies=[Depends(require_roles(["TEACHER", "ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_students_by_faculty_and_section(
    faculty_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    student_service = StudentService(session=session)
    return await student_service.get_all_student_by_section_and_faculty_id(faculty_id=faculty_id, section_id=section_id)


@student_route.delete("/admin/{student_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    student_service = StudentService(session=session)
    return await student_service.delete_student_by_student_id(student_id=student_id)


@student_route.get("/student_course", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def courses_for_student(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_course_for_student(student=user)

@student_route.post("/student_course_select", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def select_course(
    selected_course_ids: List[int],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
): 
    course_service = CourseService(session=session)
    return await course_service.course_selection_for_student(student=user, student_selected_course_ids=selected_course_ids)

@student_route.post("/admin/custom_course_student/{student_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def custom_course_add(
    student_id: str,
    course_ids: List[int],
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.custom_course_add_for_student(student_id=student_id, course_ids=course_ids)

@student_route.get("/student_course_select_", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_courses_for_student(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_courses_that_student_can(student=user)

@student_route.delete("/admin/section/{section_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student_courses_in_section(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_student_courses_by_id(section_id=section_id)

@student_route.delete("/admin/section/{section_id}/student/{student_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student_courses_by_student_id(
    section_id: int,
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_student_courses_by_id(section_id=section_id, student_id=student_id)


@student_route.delete("/admin/section/{section_id}/student/{student_id}/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student_courses_by_student_id(
    section_id: int,
    student_id: str,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_student_courses_by_id(section_id=section_id, student_id=student_id, course_id=course_id)


@student_route.get("/admin/student/{student_id}", response_model=StudentCoursesOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_student_and_courses(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_student_and_courses_by_student_id(student_id=student_id)

@student_route.get("/profile/{user_id}", dependencies=[Depends(require_roles(["STUDENT"]))], status_code=status.HTTP_200_OK)
async def user_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_service = StudentService(session=session)
    return await user_service.get_student_profile(user=user)

    


