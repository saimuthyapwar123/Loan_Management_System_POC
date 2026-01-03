from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    k: int = Field(default=3, ge=1, le=10)
