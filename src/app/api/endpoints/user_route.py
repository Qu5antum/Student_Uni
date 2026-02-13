from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.user import PersonelCreate, StudentCreate, StudentCourse, StudentOut
from src.app.service.user_service import *
from src.app.api.dependencies.check_role import require_roles
from src.app.database.models import User
from src.app.api.dependencies.dependency import get_current_user


user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


@user_route.post("/register_personel", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_personel(
    user: PersonelCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_personel(session=session, personel=user)


@user_route.post("/register_student", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_student(
    user: StudentCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_student(session=session, student=user)


@user_route.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credents: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    return await auth_user(session=session, credents=credents)


@user_route.post(
        "/", 
        response_model=StudentOut, 
        dependencies=[Depends(require_roles(["ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_student_info(
    student: StudentCourse,
    session: AsyncSession = Depends(get_session)
):
    return await get_student_by_info(session=session, user=student)

@user_route.get(
        "/", 
        response_model=List[StudentOut], 
        dependencies=[Depends(require_roles(["ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_students_in_faculty_and_section(
    faculty_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_all_student_by_section_and_faculty_id(session=session, faculty_id=faculty_id, section_id=section_id)

