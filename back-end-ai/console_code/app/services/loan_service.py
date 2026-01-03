from typing import List
from fastapi import HTTPException
from console_code.app.config.settings import DEFAULT_RATES
from console_code.app.database.db import loans_col,repayments_col
from console_code.app.utils.emi_calculator import calculate_emi, generate_schedule_per_month
from datetime import date, datetime
from bson import ObjectId
from console_code.app.exceptions.custom_exceptions import LoanAlreadyStatus, LoanNotFound, InvalidLoanOperation
from console_code.app.log.logger import get_logger
from console_code.app.utils.decorators import log_execution_time
from console_code.app.database.db import admin_col, borrower_col

logger = get_logger("loan_repayments_col")



@log_execution_time
async def apply_loan(payload: dict) -> dict:
    # -------- Role check (STRICT) --------
    if payload.get("role") != "BORROWER":
        raise HTTPException(
            status_code=403,
            detail="Only BORROWER can apply for loans"
        )

    customer_id = payload["customer_id"]
    requested_loan_type = payload.get("loan_type")

    # -------- Active loan rules --------
    blocked_statuses = ["APPLIED", "APPROVED", "DISBURSED"]

    cursor = loans_col.find(
        {
            "customer_id": customer_id,
            "status": {"$in": blocked_statuses}
        },
        {"loan_type": 1, "status": 1}
    )

    active_loans = await cursor.to_list(length=None)
    active_count = len(active_loans)

    # ❌ Rule 1: More than 2 active loans not allowed
    if active_count >= 2:
        raise HTTPException(
            status_code=400,
            detail=(
                "You already have two active loans. "
                "Please close or complete one loan before applying again."
            )
        )

    # ❌ Rule 2: Same loan type not allowed
    for loan in active_loans:
        if loan["loan_type"] == requested_loan_type:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"You already have an active {requested_loan_type} loan. "
                    "You cannot apply for the same loan type again."
                )
            )

    # -------- Loan rate --------
    annual_rate = payload.get("annual_rate") or DEFAULT_RATES.get(requested_loan_type, 9.0)

    # -------- Safe start_date handling --------
    start_date = payload.get("start_date")
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    else:
        start_date = date.today()

    # -------- EMI & amortization --------
    emi = calculate_emi(
        payload["principal"],
        annual_rate,
        payload["tenure_months"]
    )

    schedule = generate_schedule_per_month(
        payload["principal"],
        annual_rate,
        payload["tenure_months"],
        start_date
    )

    total_interest = sum(m["interest_component"] for m in schedule)
    total_late_fee = sum(m.get("late_fee", 0) for m in schedule)

    total_payable = float(payload["principal"]) + total_interest + total_late_fee

    # -------- Prepare loan document --------
    doc = {
        "customer_id": customer_id,
        "loan_type": requested_loan_type,
        "credit_score": int(payload["credit_score"]),
        "principal": float(payload["principal"]),
        "annual_rate": float(annual_rate),
        "tenure_months": int(payload["tenure_months"]),

        "status": "APPLIED",
        "applied_at": datetime.utcnow(),

        "emi_amount": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payable": round(total_payable, 2),
        "remaining_balance": round(total_payable, 2),

        "emi_schedule": schedule
    }

    # -------- Insert into MongoDB --------
    result = await loans_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return doc

async def get_loan(loan_id: str):
    doc = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise LoanNotFound(loan_id)
    doc["id"] = str(doc["_id"])
    return doc

@log_execution_time
async def approve_loan(loan_id: str, admin_id: str):
    # Fetch loan
    doc = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise LoanNotFound(loan_id)

    # If loan is already DISBURSED
    if doc["status"] in ["APPROVED", "DISBURSED", "REJECTED"]:
        raise LoanAlreadyStatus(f"Loan {loan_id} is already {doc['status']}")

    # Only APPLIED loans can be approved
    if doc["status"] != "APPLIED":
        raise InvalidLoanOperation("Only APPLIED loans can be approved")
    
    # Validate ObjectId
    try:
        oid = ObjectId(admin_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid admin ID format")

    # Fetch admin
    admin_doc = await admin_col.find_one({"_id": oid})
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Approve loan
    admin_name = f"{admin_doc.get('first_name', '')} {admin_doc.get('last_name', '')}".strip()

    # Update status to APPROVED
    await loans_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "status": "APPROVED",
                "approved_at": datetime.utcnow(),
                "approved_by_admin": str(admin_name),
            }
        },
    )

    # Return updated loan
    await get_loan(loan_id)
    
    return {"message": f"Successfully loan id {loan_id} APPROVED by admin {admin_name}"}


@log_execution_time
async def disburse_loan(loan_id: str, admin_id: str):
    doc = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise LoanNotFound(loan_id)

    if doc["status"] != "APPROVED":
        if doc["status"] == "DISBURSED":
            raise LoanAlreadyStatus(f"Loan {loan_id} is already DISBURSED")
        if doc["status"] == "REJECTED":
            raise LoanAlreadyStatus(f"Loan {loan_id} is REJECTED and cannot be disbursed")
        raise InvalidLoanOperation("Only APPROVED loans can be disbursed")

    oid = ObjectId(admin_id)
    admin_doc = await admin_col.find_one({"_id": oid})
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin_name = f"{admin_doc.get('first_name', '')} {admin_doc.get('last_name', '')}".strip()

    await loans_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "status": "DISBURSED",
                "disbursed_at": datetime.utcnow(),
                "disbursed_by_admin": admin_name,   # ✅ WHO DISBURSED
            }
        },
    )

    return {
        "message": f"Loan {loan_id} disbursed by {admin_name}",
        "disbursed_by": admin_name
    }

@log_execution_time
async def record_repayment(
    loan_id: str,
    amount: float,
    customer_id: str,
    paid_on: datetime = None
):
    paid_on = paid_on or datetime.utcnow()

    loan = await loans_col.find_one(
        {
            "_id": ObjectId(loan_id),
            "customer_id": customer_id  # 🔐 ownership check
        }
    )

    if not loan:
        raise LoanNotFound(f"Loan not found or access denied: {loan_id}")

    if loan["status"] == "CLOSED":
        raise LoanAlreadyStatus(f"Loan {loan_id} is CLOSED")

    if loan["status"] != "DISBURSED":
        raise InvalidLoanOperation("Only DISBURSED loans accept repayments")

    outstanding = round(float(loan.get("remaining_balance", 0.0)), 2)
    payment = round(float(amount), 2)

    if payment <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")

    if payment > outstanding:
        raise HTTPException(
            status_code=400,
            detail=f"Payment exceeds outstanding balance ({outstanding})"
        )

    new_outstanding = round(outstanding - payment, 2)

    # Record repayment
    await repayments_col.insert_one({
        "loan_id": loan["_id"],
        "customer_id": customer_id,
        "amount": payment,
        "paid_on": paid_on,
        "remaining_balance": new_outstanding
    })

    update = {"remaining_balance": new_outstanding}

    if new_outstanding == 0.0:
        update["status"] = "CLOSED"
        update["closed_at"] = datetime.utcnow()

    await loans_col.update_one(
        {"_id": loan["_id"]},
        {"$set": update}
    )

    logger.info(
        f"Loan {loan_id} paid {payment}, remaining {new_outstanding}"
    )

    return {
        "loan_id": loan_id,
        "paid": payment,
        "remaining_balance": new_outstanding,
        "status": update.get("status", loan["status"])
    }


@log_execution_time
async def reject_loan(loan_id: str, admin_id: str, reason: str = None):
    # Validate ObjectId
    if not ObjectId.is_valid(loan_id):
        raise HTTPException(status_code=400, detail=f"Invalid loan ID: {loan_id}")

    # Fetch loan
    loan = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise LoanNotFound(detail=f"Loan {loan_id} not found")

    # Block if already APPROVED, DISBURSED, or REJECTED
    if loan["status"] in ["APPROVED", "DISBURSED", "REJECTED"]:
       raise LoanAlreadyStatus(f"Loan {loan_id} is already {loan['status']} and cannot be rejected")

    # Only APPLIED loans can be rejected
    if loan["status"] != "APPLIED":
        raise InvalidLoanOperation(detail="Only APPLIED loans can be rejected")
    
    # Validate ObjectId
    try:
        oid = ObjectId(admin_id)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid loan ID: {admin_id}")

    # Fetch admin
    admin_doc = await admin_col.find_one({"_id": oid})
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Approve loan
    admin_name = f"{admin_doc.get('first_name', '')} {admin_doc.get('last_name', '')}".strip()

    # Update loan to REJECTED
    await loans_col.update_one(
        {"_id": loan["_id"]},
        {"$set": {
            "status": "REJECTED",
            "rejected_at": datetime.utcnow(),
            "rejected_by_admin": admin_name,
            "rejection_reason": reason
        }}
    )

    await get_loan(loan_id)


    # Return updated loan
    return {"message": f"Successfully loan id {loan_id} REJECTED by admin {admin_name}"}
