from datetime import datetime, timedelta
from app.config.settings import JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, JWT_SECRET
from jose import JWTError,jwt

# pip install python-jose[cryptography] - Library to create and verify JWTs
# pip install passlib[bcrypt] - securely hash passwords using bcrypt

def create_access_token(data:str):
    """Generate a JWT token."""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        to_encode.update({"exp":expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    except JWTError:
        return None
    
def verify_access_token(token: str):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None