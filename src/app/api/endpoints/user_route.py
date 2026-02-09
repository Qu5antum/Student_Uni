from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession



user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


"""@user_route.post("/register", status_code=status.HTTP_201_CREATED)
async def new_user(
    user: 
)"""