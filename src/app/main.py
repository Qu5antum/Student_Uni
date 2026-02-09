from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, asyncio

from src.app.database.db import init_models
from src.app.core.config import settings
from src.app.api.endpoints.user_route import user_route


app = FastAPI(
    title = settings.app_name,
    debug=settings.debug,
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(user_route)


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(
        "src.app.main:app", host="127.0.0.1", port=8000, reload=True
)
