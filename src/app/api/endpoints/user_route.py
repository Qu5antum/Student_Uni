from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from src.app.database.db import get_session, AsyncSession
from src.app.api.schemas.user import PersonelCreate, StudentCreate, StudentCourse, StudentOut
from src.app.service.user_service import *
from src.app.service.course_service import get_course_for_student, course_selection_for_student, get_student_courses_, delete_student_courses_by_id, custom_course_add_for_student
from src.app.api.dependencies.check_role import require_roles
from src.app.database.models import User
from src.app.api.dependencies.dependency import get_current_user


user_route = APIRouter(
    prefix="/user",
    tags=['users']
)


@user_route.post("/register_personel", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_personel(
    user: PersonelCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_personel(session=session, personel=user)


@user_route.post("/register_student", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_201_CREATED)
async def new_student(
    user: StudentCreate,
    session: AsyncSession = Depends(get_session)
):
    return await add_new_student(session=session, student=user)


@user_route.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credents: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    return await auth_user(session=session, credents=credents)


@user_route.post(
        "/", 
        response_model=StudentOut, 
        dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_student_info(
    student: StudentCourse,
    session: AsyncSession = Depends(get_session)
):
    return await get_student_by_info(session=session, user=student)


@user_route.get(
        "/", 
        response_model=List[StudentOut], 
        dependencies=[Depends(require_roles(["ADMIN"]))], 
        status_code=status.HTTP_200_OK
)
async def get_students_in_faculty_and_section(
    faculty_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await get_all_student_by_section_and_faculty_id(session=session, faculty_id=faculty_id, section_id=section_id)


@user_route.delete("/", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await delete_student_by_student_id(session=session, student_id=student_id)


@user_route.get("/student_course", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def courses_for_student(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await get_course_for_student(session=session, student=user)

@user_route.post("/student_course_select", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def select_course(
    selected_course_ids: List[int],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
): 
    return await course_selection_for_student(session=session, student=user, student_selected_course_ids=selected_course_ids)

@user_route.post("/custom_course_student", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def custom_course_add(
    student_id: str,
    course_ids: List[int],
    session: AsyncSession = Depends(get_session)
):
    return await custom_course_add_for_student(session=session, student_id=student_id, course_ids=course_ids)

@user_route.get("/student_course_select_", dependencies=[Depends(require_roles(["STUDENT", "ADMIN"]))], status_code=status.HTTP_200_OK)
async def get_student_courses(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await get_student_courses_(session=session, student=user)

@user_route.delete("/delet_student_courses/", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student_courses_in_section(
    section_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_student_courses_by_id(session=session, section_id=section_id)

@user_route.delete("/delet_student_courses", dependencies=[Depends(require_roles(["ADMIN"]))], status_code=status.HTTP_200_OK)
async def delete_student_courses_by_student_id(
    student_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await delete_student_courses_by_id(session=session, student_id=student_id)
