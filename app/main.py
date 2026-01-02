# app/main.py
from fastapi import FastAPI

from app.controller.movies import router as movies_router
from app.exceptions.app_exceptions import AppException
from app.exceptions.handlers import app_exception_handler
from app.core.logging_config import logger as app_logger  # فقط برای اعمال تنظیمات logging


app = FastAPI(
    title="Movie Rating System",
    version="1.0.0",
)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(movies_router)
