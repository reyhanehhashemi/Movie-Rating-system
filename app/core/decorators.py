# app/core/decorators.py
import time
import logging
from functools import wraps

logger = logging.getLogger("movie_rating")


def log_endpoint(name: str):
    """
    Decorator برای لاگ کردن اجرای endpoint ها (همه sync):

    - شروع اجرا
    - پایان اجرا + مدت زمان (ms)
    - در صورت خطا: لاگ error به همراه مدت زمان
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.info(f"{name} - started")

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                logger.info(f"{name} - finished in {duration:.2f} ms")
                return result

            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.error(
                    f"{name} - failed after {duration:.2f} ms: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator
