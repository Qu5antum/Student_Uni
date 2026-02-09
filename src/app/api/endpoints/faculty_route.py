from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.faculty import FacultyCreate
from src.app.service.faculty_service import add_new_faculty


faculty_route = APIRouter(
    prefix="/faculty",
    tags=['facultys']
)


@faculty_route.post("/", status_code=status.HTTP_201_CREATED)
async def add_new_faculty(
    faculty: FacultyCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_faculty(session=session, faculty=faculty)


