from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime

class LoanApplyRequest(BaseModel):
    loan_type: Literal["PROPERTY","EDUCATION","GOLD","VEHICLE"]
    credit_score: int
    principal: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    annual_rate: Optional[float] = None
    start_date: Optional[datetime] = None

    
    @validator("credit_score")
    def validate_credit_score(cls, v):
        """
        Credit Score Validation (CIBIL Standard: 650 - 900)
        """
        if not isinstance(v, int):
            raise HTTPException(status_code=400, detail="Credit score must be an integer")

        if v < 650 or v > 900:
            raise HTTPException(
                status_code=400,
                detail="Invalid credit score. Must be between 650 and 900"
            )
        return v


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