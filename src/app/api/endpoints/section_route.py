from fastapi import APIRouter, status, Depends

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.section import SectionCreate
from src.app.service.section_service import add_new_section, get_section_by_id, delete_section_by_id
from src.app.api.dependencies.check_role import require_roles

section_route = APIRouter(
    prefix="/faculty/{faculty_id}/section",
    tags=['sections']
)


@section_route.post("/new_section", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_section(
    section: SectionCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_section(session=session, section=section)


@section_route.get("/", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_section(
    faculty_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_section_by_id(session=session, faculty_id=faculty_id)


@section_route.get("/{section_id}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_section(
    faculty_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_section_by_id(session=session, faculty_id=faculty_id, section_id=section_id)


@section_route.delete("/{section}", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_section(
    faculty_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_section_by_id(session=session, faculty_id=faculty_id, section_id=section_id)