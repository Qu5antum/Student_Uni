from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.course import CourseCreate
from src.app.service.course_service import add_new_course, get_course_by_id, delete_course_id
from src.app.api.dependencies.check_role import require_roles


course_route = APIRouter(
    prefix="/course",
    tags=['courses']
)


@course_route.post("/new_course", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_course(session=session, course=course)


@course_route.get("/", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_course(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_course_by_id(session=session, section_id=section_id)
    

@course_route.get("/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_course(
    section_id: int,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_course_by_id(session=session, section_id=section_id, course_id=course_id)


@course_route.delete("/{course_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_course(
    section_id: int,
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_course_id(session=session, section_id=section_id, course_id=course_id)