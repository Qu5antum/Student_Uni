from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from src.app.exceptions.base import AppException
from src.app.api.schemas.error_responce import ErrorResponce


async def app_exception_handler(
        request: Request,
        exc: AppException
) -> JSONResponse:
    error = jsonable_encoder(ErrorResponce(status_code=exc.status_code, er_message=exc.message, er_details=exc.details))
    return JSONResponse(status_code=exc.status_code, content=error)


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["msg"]
                } 
                for err in exc.errors()
            ]
        }
    )