from bson import ObjectId
from fastapi import Depends, HTTPException,status
import inspect
from functools import wraps
from time import time
from app.log.logger import get_logger
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt_handler import verify_access_token
from app.database.db import admin_col, borrower_col  

logger = get_logger("log_execution_time")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


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


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_access_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Validate ObjectId format
        try:
            oid = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user_id in token")

        # Check Admins
        admin_user = await admin_col.find_one({"_id": oid})
        if admin_user:
            return {"role": "ADMIN", "user": admin_user}

        # Check Borrowers
        borrower_user = await borrower_col.find_one({"_id": oid})
        if borrower_user:
            return {"role": "BORROWER", "user": borrower_user}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")



def require_role(roles:list[str]):
    async def role_checker(user = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail= f"Access forbidden: Requires one of {roles} roles")
        return user
    return role_checker
