from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.course import CourseCreate, CourseUpdate, CourseOut
from src.app.service.course_service import CourseService, StudentCourseService
from src.app.service.course_service import *
from src.app.api.dependencies.check_role import require_roles

course_route = APIRouter(
    prefix="/api/course",
    tags=['courses']
)


@course_route.post("/admin/new_course", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.add_new_course(course=course)


@course_route.get("/admin/section/{section_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_course(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_course_by_id(section_id=section_id)
    

@course_route.get("/admin/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_course(
    section_id: int,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_course_by_id(section_id=section_id, course_id=course_id)


@course_route.get("/admin/course/{course_code}", response_model=CourseOut, dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_course_by_code(
    course_code: str,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.get_course_by_course_code(course_code=course_code)


@course_route.put("/admin/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.update_course_by_id(course_id=course_id, course_update=course_update)


@course_route.delete("/admin/course/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_course(
    section_id: int,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = CourseService(session=session)
    return await course_service.delete_course_id(section_id=section_id, course_id=course_id)


@course_route.get("/admin/course/students/{course_id}", dependencies=[Depends(require_roles(["TEACHER", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_student_numbers_of_course(
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    course_service = StudentCourseService(session=session)
    return await course_service.numbers_of_student_of_current_course(course_id=course_id)



