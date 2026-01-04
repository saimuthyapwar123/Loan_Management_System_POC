from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    thread_id: Optional[str] = None
    # k: int = Field(default=3, ge=1, le=10)

