from typing import Literal
from pydantic import BaseModel


class TokenModel(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    borrower_id: str | None = None