from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.database.db import get_session, AsyncSession
from src.app.service.user_service import auth_user

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
