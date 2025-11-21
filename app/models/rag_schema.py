from pydantic import BaseModel
from typing import List


class Query(BaseModel):
    query: str


class QueryRequest(BaseModel):
    query: str
    customer_id: str
    k: int = 3

