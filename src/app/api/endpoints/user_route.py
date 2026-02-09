from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.user import PersonelCreate
from src.app.service.user_service import add_new_personel


user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


@user_route.post("/register_personel", status_code=status.HTTP_201_CREATED)
async def new_user(
    user: PersonelCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_personel(session=session, personel=user)