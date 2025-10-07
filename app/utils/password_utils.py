from passlib.context import CryptContext
import re

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_content.hash(password)

def verify_password(plain:str, hashed:str) -> bool:
    return pwd_content.verify(plain, hashed)

def is_strong_password(p: str) -> bool:
    """DOB must be exactly 8 characters (YYYYMMDD)."""
    return bool(re.fullmatch(r"\d{8}", p))