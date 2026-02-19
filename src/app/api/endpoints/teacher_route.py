from fastapi import APIRouter, status, Depends
from typing import List

from src.app.database.db import AsyncSession, get_session
from src.app.api.dependencies.check_role import require_roles
from src.app.api.schemas.user import TeacherCreate, TeacherOut
from src.app.service.teacher_service import add_new_teacher, get_all_teacher

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


@teacher_route.get("/admin/teacher", response_model=List[TeacherOut], dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_teacher(
    session: AsyncSession = Depends(get_session)
):
    return await get_all_teacher(session=session)
