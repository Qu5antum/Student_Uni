from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID

from src.app.database.db import AsyncSession, get_session
from src.app.database.models import User
from src.app.api.dependencies.dependency import get_current_user
from src.app.api.dependencies.check_role import require_roles
from src.app.api.schemas.user import TeacherCreate, TeacherOut, StudentOut
from src.app.api.schemas.course import TeacherCoursesOut, CourseOut
from src.app.service.course_service import CourseService
from src.app.service.teacher_service import TeacherService

teacher_route = APIRouter(
    prefix="/api/user/teacher",
    tags=["teachers"]
)


@teacher_route.post("/admin/register_teacher", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_personel(
    user: TeacherCreate,
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.add_new_teacher(personel=user)


@teacher_route.get("/admin", response_model=List[TeacherOut], dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teacher(
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.get_all_teacher()

@teacher_route.get("/admin/{teacher_id}", response_model=TeacherOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teacher_by_id(
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.get_all_teacher(teacher_id=teacher_id)


@teacher_route.delete("/admin/{teacher_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_teacher(
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.delete_teacher_by_user_id(teacher_id=teacher_id)


@teacher_route.post("/admin/{teacher_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def add_course_for_teacher(
    course_ids: List[int],
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.add_course_for_teacher_by_teacher_id(teacher_id=teacher_id, course_ids=course_ids)


@teacher_route.get("/admin/courses/{teacher_id}", response_model=TeacherCoursesOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teachers_courses(
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_courses_of_teacher_by_id(teacher_id=teacher_id)


@teacher_route.delete("/admin/section/{section_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_courses_of_teacher_in_section(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_courses_of_teacher_by_id(section_id=section_id)


@teacher_route.delete("/admin/section/{section_id}/teacher/{teacher_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_courses_of_teacher_in_section_by_teacher_id(
    section_id: int,
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_courses_of_teacher_by_id(section_id=section_id, teacher_id=teacher_id)


@teacher_route.delete("/admin/section/{section_id}/teacher/{teacher_id}/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_specific_course_of_teacher_in_section_by_teacher_id(
    section_id: int,
    teacher_id: UUID,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_courses_of_teacher_by_id(section_id=section_id, teacher_id=teacher_id, course_id=course_id)


@teacher_route.get("/teacher/{teacher_id}", response_model=List[CourseOut], dependencies=[Depends(require_roles(["TEACHER", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def teacher_courses(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.teacher_courses_by_user_id(teacher=user)


@teacher_route.get("/teacher/course/{course_id}", response_model=List[StudentOut], dependencies=[Depends(require_roles(["TEACHER", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def teacher_list_students_of_course(
    course_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    teacher_service = TeacherService(session=session)
    return await teacher_service.list_student_of_courses_by_course_id(course_id=course_id, teacher=user)







