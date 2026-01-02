# app/core/logging_config.py
import logging

# اسم logger اصلی سرویس
LOGGER_NAME = "movie_rating"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# جلوی اضافه شدن چندباره‌ی handler را می‌گیریم
if not logger.handlers:
    handler = logging.StreamHandler()  # خروجی روی stdout (لاگ‌های Uvicorn/Docker)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
