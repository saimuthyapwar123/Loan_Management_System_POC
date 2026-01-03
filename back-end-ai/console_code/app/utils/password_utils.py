from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72
YYYYMMDD_REGEX = re.compile(r"^\d{8}$")


def is_strong_password(password: str) -> bool:
    """
    Password must be exactly 8 digits in YYYYMMDD format.
    """
    return isinstance(password, str) and bool(YYYYMMDD_REGEX.fullmatch(password))


def hash_password(password: str) -> str:
    """
    Hash password safely during registration.
    """
    if not is_strong_password(password):
        raise ValueError("Password must be in YYYYMMDD format")

    password = password.strip()

    if len(password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("Password too long for bcrypt")

    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify password safely during login.
    NEVER raises bcrypt errors.
    """
    try:
        if not is_strong_password(plain):
            return False

        plain = plain.strip()

        if len(plain.encode("utf-8")) > MAX_BCRYPT_BYTES:
            return False

        return pwd_context.verify(plain, hashed)

    except Exception:
        return False


# def hash_password(password:str) -> str:
#     return pwd_content.hash(password)

# def verify_password(plain:str, hashed:str) -> bool:
#     return pwd_content.verify(plain, hashed)

# def is_strong_password(p: str) -> bool:
#     """DOB must be exactly 8 characters (YYYYMMDD)."""
#     return bool(re.fullmatch(r"\d{8}", p))