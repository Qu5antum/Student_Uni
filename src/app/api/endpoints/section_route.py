from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.section import SectionCreate
from src.app.service.section_service import add_new_section
from src.app.api.dependencies.check_role import require_roles

section_route = APIRouter(
    prefix="/section",
    tags=['sections']
)


@section_route.post("/new_section", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_section(
    section: SectionCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_section(session=session, section=section)
    