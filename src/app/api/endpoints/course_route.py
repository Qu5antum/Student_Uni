from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.course import CourseCreate
from src.app.service.course_service import add_new_course
from src.app.api.dependencies.check_role import require_roles


course_route = APIRouter(
    prefix="/course",
    tags=['courses']
)


course_route("/new_course", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_course(session=session, course=course)