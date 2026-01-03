from bson import ObjectId
from fastapi import Depends, HTTPException,status
import inspect
from functools import wraps
from time import time
from ai_chatbot.app.log.logger import get_logger
from fastapi.security import OAuth2PasswordBearer
# from app.utils.jwt_handler import decode_access_token
# from ai_chatbot.app.database.db import admin_col, borrower_col  

logger = get_logger("log_execution_time")


def log_execution_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            execution_time_ms = round((time() - start_time) * 1000, 2)
            logger.info(f"{func.__name__} executed in {execution_time_ms} ms")
            return result

        except HTTPException as http_exc:
            logger.warning(f"Handled HTTPException in {func.__name__}: {http_exc.status_code} - {http_exc.detail}")
            raise http_exc

        except Exception as e:
            logger.exception(f"Unexpected exception in {func.__name__}: {str(e)}")
            raise e

    return wrapper

