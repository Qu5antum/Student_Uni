from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.faculty import FacultyCreate
from src.app.service.faculty_service import add_new_faculty, delete_faculty_by_id
from src.app.api.dependencies.check_role import require_roles


faculty_route = APIRouter(
    prefix="/faculty",
    tags=['facultys']
)


@faculty_route.post("/new_faculty", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_faculty(
    faculty: FacultyCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_faculty(session=session, faculty=faculty)


@faculty_route.delete("/{faculty_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_faculty(
    faculty_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_faculty_by_id(session=session, faculty_id=faculty_id)


