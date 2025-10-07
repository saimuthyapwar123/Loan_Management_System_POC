from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class LoanApplyRequest(BaseModel):
    loan_type: Literal["PROPERTY","EDUCATION","GOLD","VEHICLE"]
    principal: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    annual_rate: Optional[float] = None
    start_date: Optional[datetime] = None

class LoanResponse(BaseModel):
    id: str  # MongoDB _id as string
    customer_id:str
    loan_type: str
    principal: float
    annual_rate: float
    tenure_months: int
    emi_amount: float
    status: str
    applied_at: datetime
    remaining_balance: float
    emi_schedule: Optional[List[dict]] = None

class RejectRequest(BaseModel):
    reason: str | None = None