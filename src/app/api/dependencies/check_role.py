from fastapi import HTTPException, status, Depends

from .dependency import get_current_user
from src.app.database.models import User


def require_roles(allowed_roles: list[str]):
    async def checker(
        current_user: User = Depends(get_current_user)
    ):
        user_roles = [role.name for role in current_user.roles]

        if not set(user_roles) & set(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient rights."
            )

        return current_user

    return checker