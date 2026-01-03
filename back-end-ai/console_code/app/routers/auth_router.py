from fastapi import APIRouter, HTTPException, Depends
from console_code.app.models.auth_schema import RegisterUser, LoginModel
from console_code.app.models.response_schema import TokenModel
from console_code.app.services.auth_service import (
    register_user,
    user_login,
    list_users
)
from console_code.app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    PasswordPolicyException
)
from console_code.app.log.logger import get_logger
from console_code.app.utils.decorators import get_current_user, require_role

router = APIRouter(prefix="/loan_auth",tags=["Authentication"])
logger = get_logger("Auth_Router")

# ======================================================
#                    ADMIN ROUTES
# ======================================================

@router.post("/admin/register")
async def admin_register(user: RegisterUser):
    try:
        user.role = "ADMIN"
        response = await register_user(user)
        logger.info(f"Admin registered: {user.username}")
        return response

    except (UserAlreadyExistsException, PasswordPolicyException) as e:
        logger.warning(f"Admin registration failed: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Admin registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Admin registration failed")


@router.post("/admin/login", response_model=TokenModel)
async def admin_login(user: LoginModel):
    try:
        user.role = "ADMIN"
        response = await user_login(
            username=user.username,
            password=user.password,
            role=user.role
        )
        logger.info(f"Admin logged in: {user.username}")
        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Admin login failed")


# ======================================================
#                  BORROWER ROUTES
# ======================================================

@router.post("/borrower/register")
async def borrower_register(user: RegisterUser):
    try:
        user.role = "BORROWER"
        response = await register_user(user)
        logger.info(f"Borrower registered: {user.username}")
        return response

    except (UserAlreadyExistsException, PasswordPolicyException) as e:
        logger.warning(f"Borrower registration failed: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Borrower registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Borrower registration failed")


@router.post("/borrower/login", response_model=TokenModel)
async def borrower_login(user: LoginModel):
    try:
        user.role = "BORROWER"
        response = await user_login(
            username=user.username,
            password=user.password,
            role=user.role
        )
        logger.info(f"Borrower logged in: {user.username}")
        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Borrower login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Borrower login failed")


# ======================================================
#                COMMON AUTH ROUTES
# ======================================================

@router.get("/auth/me")
async def get_me(current=Depends(get_current_user)):
    user = current.get("user")
    role = current.get("role")

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info(f"Current user fetched: {user.get('username')}")

    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "email": user.get("email"),
        "aadhar_number": user.get("aadhar_number"),
        "pan_number": user.get("pan_number"),
        "dob": user.get("dob"),
        "address": user.get("address"),
        "role": role
    }


@router.get(
    "/admin/users",
    dependencies=[Depends(require_role("ADMIN"))]
)
async def get_users(role: str):
    users = await list_users(role)
    logger.info(f"Admin fetched users of role: {role}")
    return users
