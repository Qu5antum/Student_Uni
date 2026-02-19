from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database.db import AsyncSession
from src.app.database.models import User, Role
from src.app.security.security_context import hash_password
from src.app.api.schemas.user import TeacherCreate

#register new teacher
async def add_new_teacher(
        session: AsyncSession, 
        personel: TeacherCreate
):
    role = await session.scalar(
        select(Role).where(Role.name == "TEACHER") 
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role not found"
        )
    
    new_user = User(
        **personel.model_dump(exclude={"password"}),
        password=hash_password(personel.password)
    )

    new_user.roles.append(role)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "Registered successfully."}


async def get_all_teacher(
        session: AsyncSession,
        teacher_id: int | None = None
):
    if not teacher_id:
        result = await session.execute(
            select(User)
            .join(User.roles)
            .where(Role.name == "TEACHER")
        ) 
        teachers = result.scalars().unique().all()

        return teachers
    
    elif teacher_id:
        result = await session.execute(
            select(User)
            .join(User.roles)
            .where(
                User.id == teacher_id,
                Role.name == "TEACHER"
            )
        )
        existing_teacher = result.scalar_one_or_none()

        if not existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher by this ID {teacher_id} not found."
            )
        
        return existing_teacher



    




