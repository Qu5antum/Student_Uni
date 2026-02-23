from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.faculty import FacultyCreate
from src.app.service.faculty_service import FacultyService
from src.app.api.dependencies.check_role import require_roles


faculty_route = APIRouter(
    prefix="/faculty",
    tags=['facultys']
)


@faculty_route.post("admin/new_faculty", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_faculty(
    faculty: FacultyCreate,
    session: AsyncSession = Depends(get_session)
):
    faculty_service = FacultyService(session=session)
    return await faculty_service.add_new_faculty(session=session, faculty=faculty)


@faculty_route.get("admin/", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_faculty(
    session: AsyncSession = Depends(get_session)
):
    faculty_service = FacultyService(session=session)
    return await faculty_service.get_faculy_by_id()


@faculty_route.get("/admin/{faculty_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_faculty(
    faculty_id: int,
    session: AsyncSession = Depends(get_session)
):
    faculty_service = FacultyService(session=session)
    return await faculty_service.get_faculy_by_id(faculty_id=faculty_id)


@faculty_route.delete("/admin/{faculty_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_faculty(
    faculty_id: int,
    session: AsyncSession = Depends(get_session)
):
    faculty_service = FacultyService(session=session)
    return await faculty_service.delete_faculty_by_id(faculty_id=faculty_id)


