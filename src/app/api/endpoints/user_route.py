from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.user import PersonelCreate, StudentCreate, UserCourse, UserOut
from src.app.service.user_service import add_new_personel, add_new_student, auth_user, get_student_by_info
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
        response_model=UserOut, 
        dependencies=[Depends(require_roles(["ADMIN"]))], 
        status_code=status.HTTP_201_CREATED
)
async def get_student_info(
    student: UserCourse,
    session: AsyncSession = Depends(get_session)
):
    return await get_student_by_info(session=session, user=student)

