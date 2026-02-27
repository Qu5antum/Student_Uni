from fastapi import APIRouter, status, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from uuid import UUID

from src.app.database.db import get_session, AsyncSession
from src.app.database.models import User
from src.app.service.user_service import AuthenticationService
from src.app.api.dependencies.dependency import get_current_user
from src.app.api.dependencies.check_role import require_roles
from src.app.service.face_setup_service import FaceRecognitionService

limiter = Limiter(key_func=get_remote_address)

user_route = APIRouter(
    prefix="/api/user",
    tags=['users']
)

@user_route.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credents: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    authentication_service = AuthenticationService(session=session)
    return await authentication_service.auth_user(credents=credents)


@user_route.post("/register_face/{user_id}", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def register_face(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.register_face_for_current_user(user=user, file=file)


@user_route.post("/recognize_face", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def recognize_face(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.recognize_user_by_face(file=file)


@user_route.delete("/admin/{user_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_face_photo_by_user_id(
    request: Request,
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.delete_face_from_db(user_id=user_id)


@user_route.delete("/delete_photo", dependencies=[Depends(require_roles(["TEACHER", "STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_face_photo_by_user_id(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    face_recognition_service = FaceRecognitionService(session=session)
    return await face_recognition_service.delete_face_from_db(user=user)

