from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.app.security.security import create_jwt_token
from src.app.security.security_context import check_hashes, hash_password
from src.app.database.db import AsyncSession
from src.app.database.models import User
from src.app.repositories.user_repository import UserRepository
from src.app.repositories.role_repository import RoleRepository
from src.app.api.schemas.user import ChangePasswordRequest, AdminCreate


class AuthenticationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session=self.session)
        self.role_repo = RoleRepository(session=self.session)

    async def create_admin(self, admin: AdminCreate):
        existing_user = await self.user_repo.get_user_from_email(email=admin.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists."
            )
        
        role = await self.role_repo.get_admin_role()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role not found."
            )
        
        new_admin = User(
            **admin.model_dump(exclude={"password"}),
            password=hash_password(admin.password)
        )

        new_admin.roles.append(role)

        try:
            self.session.add(new_admin)
            await self.session.commit()
            await self.session.refresh(new_admin)
        except:
            await self.session.rollback()
            raise
        
        return {"message": "Registered successfully."} 
        
    # authenticate user 
    async def auth_user(
            self,
            credents: OAuth2PasswordRequestForm
    ):
        user = await self.user_repo.get_user_from_email(email=credents.username)
        
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

    async def change_password(self, data: ChangePasswordRequest, user: User):
        if not check_hashes(data.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )
        
        if data.new_password != data.new_password_again:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords not match."
            )
        
        user = await self.user_repo.update_password(user_id=user.id, new_password=data.new_password)

        return {"detail": "Password successfully changed."}



