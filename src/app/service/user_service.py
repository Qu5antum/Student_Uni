from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.app.security.security import create_jwt_token
from src.app.security.security_context import check_hashes
from src.app.database.db import AsyncSession
from src.app.database.models import User



#async def add_new_user(session: AsyncSession, user: )


# authenticate user 
async def auth_user(credents: OAuth2PasswordRequestForm, session: AsyncSession):
    query = select(User).where(User.username == credents.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    if not check_hashes(credents.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
    
    token = await create_jwt_token({"sub": str(user.id)})
    return {"access_token": token,
            "token_type": "bearer"}