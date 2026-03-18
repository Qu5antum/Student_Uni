from uuid import UUID
from sqlalchemy import select

from .base_repository import BaseRepository
from src.app.database.models import User, Faculty, Section, Role


class UserRepository(BaseRepository):
    model = User

    async def get_student_profile(self, user_id: UUID):
        result = await self.session.execute(
            select(
                self.model.name,
                self.model.surname,
                self.model.email,
                self.model.student_id,
                self.model.class_,
                Faculty.name.label("faculty_name"), 
                Section.name.label("section_name")
            )
            .join(self.model.roles)
            .join(self.model.faculty)
            .join(self.model.section)
            .where(
                self.model.id == user_id,
                Role.name == "STUDENT"
            )
        )

        return result.mappings().one_or_none()
    
    async def get_teacher_profile(self, user_id: UUID):
        result = await self.session.execute(
            select(
                self.model.name,
                self.model.surname,
                self.model.email,
                Faculty.name.label("faculty_name"), 
            )
            .join(self.model.roles)
            .join(self.model.faculty)
            .where(
                self.model.id == user_id,
                Role.name == "TEACHER"
            )
        )

        return result.mappings().one_or_none()

        

