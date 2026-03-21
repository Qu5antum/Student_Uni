from src.app.database.models import Course
from .base_repository import BaseRepository


class CourseRepository(BaseRepository):
    model = Course