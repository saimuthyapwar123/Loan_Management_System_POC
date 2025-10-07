from fastapi import APIRouter, HTTPException, Depends
from app.models.auth_schema import RegisterUser, LoginModel
from app.models.response_schema import TokenModel
from app.services.auth_service import  list_users, register_user, user_login
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException, PasswordPolicyException
)
from app.log.logger import get_logger
from app.utils.decorators import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("User_Registration_Login")


# ---------------- User Register ----------------
@router.post("/register")
async def register(user: RegisterUser):
    try:
        response = await register_user(user)
        logger.info(f" Successfully registered: {user.username}")
        return response

    except (UserAlreadyExistsException, PasswordPolicyException) as e:
        logger.warning(f" Registration failed for {user.username}: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f" Registration error for {user.username}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="User failed to register. Please try again."
        )


# ---------------- User Login ----------------
@router.post("/login", response_model=TokenModel)
async def login(user: LoginModel):
    try:
        response = await user_login(user.username, user.password,user.role)
        logger.info(f" Successfully logged in: {user.username} with role {user.role}")
        return response

    except HTTPException as e:
        logger.warning(f" Login failed for {user.username}: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f" Unexpected login failure for {user.username}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="User failed to login. Please try again."
        )

# ---------------- Current User Info ----------------
@router.get("/me")
async def me(current=Depends(get_current_user)):
    user_doc = current.get("user")  # actual MongoDB document
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid token: missing user data")
    
    logger.info(f"Current user is {user_doc.get("username")} with role {current.get("role")}")
    return {
        "id": str(user_doc["_id"]),
        "username": user_doc.get("username"),
        "role": current.get("role")
    }

# ---------------- Admin-only Route ----------------
@router.get("/users")
async def list_all_users(role:str , admin=Depends(require_role("ADMIN"))):
    users = await list_users(role)
    for u in users:
        u.pop("password_hash", None)

    logger.info(f"user data with role {role} is fetch")
    return users
