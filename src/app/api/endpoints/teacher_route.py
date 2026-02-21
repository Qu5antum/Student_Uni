from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID

from src.app.database.db import AsyncSession, get_session
from src.app.database.models import User
from src.app.api.dependencies.dependency import get_current_user
from src.app.api.dependencies.check_role import require_roles
from src.app.api.schemas.user import TeacherCreate, TeacherOut
from src.app.api.schemas.course import TeacherCoursesOut, CourseOut
from src.app.service.teacher_service import add_new_teacher, get_all_teacher, teacher_courses_by_user_id
from src.app.service.course_service import add_course_for_teacher_by_teacher_id, get_courses_of_teacher_by_id, delete_courses_of_teacher_by_id

teacher_route = APIRouter(
    prefix="/user/teacher",
    tags=["teachers"]
)


@teacher_route.post("/admin/register_teacher", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_personel(
    user: TeacherCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_teacher(session=session, personel=user)


@teacher_route.get("/admin", response_model=List[TeacherOut], dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teacher(
    session: AsyncSession = Depends(get_session)
):
    return await get_all_teacher(session=session)

@teacher_route.get("/admin/{teacher_id}", response_model=TeacherOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teacher_by_id(
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    return await get_all_teacher(session=session, teacher_id=teacher_id)


@teacher_route.post("/admin/{teacher_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def add_course_for_teacher(
    course_ids: List[int],
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    return await add_course_for_teacher_by_teacher_id(session=session, teacher_id=teacher_id, course_ids=course_ids)


@teacher_route.get("/admin/courses/{teacher_id}", response_model=TeacherCoursesOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teachers_courses(
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    return await get_courses_of_teacher_by_id(session=session, teacher_id=teacher_id)


@teacher_route.delete("/admin/section/{section_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_courses_of_teacher_in_section(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_courses_of_teacher_by_id(session=session, section_id=section_id)


@teacher_route.delete("/admin/section/{section_id}/teacher/{teacher_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_courses_of_teacher_in_section_by_teacher_id(
    section_id: int,
    teacher_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    return await delete_courses_of_teacher_by_id(session=session, section_id=section_id, teacher_id=teacher_id)


@teacher_route.delete("/admin/section/{section_id}/teacher/{teacher_id}/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_specific_course_of_teacher_in_section_by_teacher_id(
    section_id: int,
    teacher_id: UUID,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_courses_of_teacher_by_id(session=session, section_id=section_id, teacher_id=teacher_id, course_id=course_id)


@teacher_route.get("/teacher/{teacher_id}", response_model=List[CourseOut], dependencies=[Depends(require_roles(["TEACHER", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def teacher_courses(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await teacher_courses_by_user_id(session=session, teacher=user)





