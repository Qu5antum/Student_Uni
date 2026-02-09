from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.app.security.security import create_jwt_token
from src.app.security.security_context import check_hashes, hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User, Role
from src.app.api.schemas.user import StudentCreate, PersonelCreate

#register new student
async def add_new_student(
        session: AsyncSession, 
        student: StudentCreate
):
    result = await session.execute(
        select(User).where(User.student_id == student.student_id)
    )

    existing_student = result.scalar_one_or_none()

    if existing_student: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this student ID already exists."
        ) 
    
    role = await session.scalar(
        select(Role).where(Role.name == "STUDENT") 
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student role not found"
        )
    
    new_user = User(
        **student.model_dump(exclude={"password"}),
        password=hash_password(student.password)
    )

    new_user.roles.append(role)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message: ", "Registered successfully."}



#register new personel
async def add_new_personel(
        session: AsyncSession, 
        personel: PersonelCreate
):
    role = await session.scalar(
        select(Role).where(Role.name == "ADMIN") 
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student role not found"
        )
    
    new_user = User(
        **personel.model_dump(exclude={"password"}),
        password=hash_password(personel.password)
    )

    new_user.roles.append(role)

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

    return {"access_token": token, "token_type": "bearer"}