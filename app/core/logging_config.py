# app/core/logging_config.py
import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
)

# logger اصلی سرویس
logger = logging.getLogger("movie_rating")
