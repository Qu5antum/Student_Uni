from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn, asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import logging

from src.app.database.db import init_models
from src.app.core.config import settings
from src.app.handlers.exception_handler import validation_exception_handler
from src.app.api.endpoints.user_route import user_route
from src.app.api.endpoints.student_route import student_route
from src.app.api.endpoints.teacher_route import teacher_route
from src.app.api.endpoints.faculty_route import faculty_route
from src.app.api.endpoints.section_route import section_route
from src.app.api.endpoints.course_route import course_route


logging.basicConfig(level=logging.INFO)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title = settings.app_name,
    debug=settings.debug,
    docs_url="/docs"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(user_route)
app.include_router(teacher_route)
app.include_router(student_route)
app.include_router(faculty_route)
app.include_router(section_route)
app.include_router(course_route)

if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(
        "src.app.main:app", host="127.0.0.1", port=8000, reload=True
)
