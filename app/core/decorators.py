# app/core/decorators.py
import time
import logging
from functools import wraps

logger = logging.getLogger("movie_rating")


def log_endpoint(name: str):
    """
    Decorator ساده برای:
    - لاگ شروع اجرای endpoint
    - لاگ پایان + مدت زمان (ms)
    - در صورت خطا: لاگ ERROR با stacktrace (exc_info=True)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.info("%s - started", name)

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                logger.info("%s - finished in %.2f ms", name, duration)
                return result

            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.error(
                    "%s - failed after %.2f ms: %s", name, duration, e, exc_info=True
                )
                raise

        return wrapper

    return decorator
