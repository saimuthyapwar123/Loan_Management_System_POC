from datetime import date
from bson import ObjectId
from console_code.app.database.db import admin_col, borrower_col
from console_code.app.utils.decorators import  log_execution_time
from console_code.app.utils.password_utils import hash_password, verify_password, is_strong_password
from console_code.app.exceptions.custom_exceptions import UserAlreadyExistsException, PasswordPolicyException
from console_code.app.utils.jwt_handler import create_access_token
from fastapi import HTTPException

@log_execution_time
async def register_user(data):
    # Check already existing user in correct collection
    if await admin_col.find_one({"username": data.username, "role": data.role}):
        raise UserAlreadyExistsException()

    if await borrower_col.find_one({"username": data.username, "role": data.role}):
        raise UserAlreadyExistsException()
    
    # Password policy
    if not is_strong_password(data.password):
        raise PasswordPolicyException()
    
    # Hash password safely (bcrypt-safe)
    try:
        hashed_password = hash_password(data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    doc = data.dict()
    doc["password"] = hashed_password  # overwrite plain password
    

    if isinstance(doc.get("dob"), date):
        doc["dob"] = doc["dob"].isoformat()


    if doc["role"] == "ADMIN":
        await admin_col.insert_one(doc)

    elif doc["role"] == "BORROWER":
        await borrower_col.insert_one(doc)

    return {"message": f"Successfully registered {data.username} as {data.role}"}


@log_execution_time
async def user_login(username: str, password: str, role: str):
    password = password.strip()

    if role == "ADMIN":
        user = await admin_col.find_one({"username": username, "role": role})
    else:
        user = await borrower_col.find_one({"username": username, "role": role})

    if not user:
        raise HTTPException(status_code=401, detail="Username or role not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    response = {
        "message": f"Login successful as {role}",
        "access_token": token,
        "token_type": "bearer"
    }

    if role == "BORROWER":
        response["borrower_id"] = str(user["_id"])

    return response


@log_execution_time
async def get_user_by_id(user_id: str, role: str):
    if role == "ADMIN":
        user = await admin_col.find_one({"_id": ObjectId(user_id)})
    else:
        user = await borrower_col.find_one({"_id": ObjectId(user_id)})

    if not user:
        return None

    user["id"] = str(user["_id"])
    user.pop("_id", None)
    return user


@log_execution_time
async def list_users(role: str):
    if role.upper() == "BORROWER":
        cursor = borrower_col.find()
    elif role.upper() == "ADMIN":
        cursor = admin_col.find()
    else:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    
    users_list = []
    async for u in cursor:
        users_list.append({
            "id": str(u["_id"]),
            "first_name": u.get("first_name"),
            "last_name": u.get("last_name"),
            "email": u.get("email"),
            "aadhar_number": u.get("aadhar_number"),
            "pan_number": u.get("pan_number"),
            "dob": u.get("dob"),
            "address": u.get("address"),
            "role":u.get("role")
        })
    return users_list