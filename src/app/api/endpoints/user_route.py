from fastapi import APIRouter, status, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from src.app.database.db import get_session, AsyncSession
from src.app.database.models import User
from src.app.service.user_service import AuthenticationService
from src.app.api.dependencies.dependency import get_current_user
from src.app.service.face_setup_service import FaceRecognitionService

user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


@user_route.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credents: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    authentication_service = AuthenticationService(session=session)
    return await authentication_service.auth_user(credents=credents)


@user_route.post("/register_face/{user_id}", status_code=status.HTTP_200_OK)
async def register_face(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.register_face_for_current_user(user=user, file=file)


@user_route.post("/recognize_face", status_code=status.HTTP_200_OK)
async def recognize_face(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.recognize_user_by_face(file=file)
