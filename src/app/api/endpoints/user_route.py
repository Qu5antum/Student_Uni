from fastapi import APIRouter, status, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from src.app.database.db import get_session, AsyncSession
from src.app.database.models import User
from src.app.service.user_service import auth_user
from src.app.api.dependencies.dependency import get_current_user
from src.app.service.face_setup_service import register_face_for_current_user, recognize_user_by_face

user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


@user_route.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credents: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    return await auth_user(session=session, credents=credents)


@user_route.post("/register_face/{user_id}", status_code=status.HTTP_200_OK)
async def register_face(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await register_face_for_current_user(session=session, user=user, file=file)


@user_route.post("/recognize_face", status_code=status.HTTP_200_OK)
async def recognize_face(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    return await recognize_user_by_face(session=session, file=file)
