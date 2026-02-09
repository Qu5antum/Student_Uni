from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.app.security.security import create_jwt_token
from src.app.security.security_context import check_hashes, hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User, Role
from src.app.api.schemas.user import UserCreate



async def add_new_student(
        session: AsyncSession, 
        user: UserCreate
):
    result = await session.execute(
        select(User).where(User.name == user.name)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this name already exists."
        ) 
    
    role = await session.scalar(
        select(Role).where(Role.name == "admin") 
    )

    if not role:
        raise ValueError("Role not found")
    
    new_user = User(
        name = user.name,
        password = hash_password(user.password),
        roles = [role]
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message: ", "Registered successfully."}




# authenticate user 
async def auth_user(
        credents: OAuth2PasswordRequestForm, 
        session: AsyncSession
):
    result = await session.execute(
        select(User).where(User.username == credents.username)
    )

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