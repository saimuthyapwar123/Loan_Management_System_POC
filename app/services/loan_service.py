from fastapi import HTTPException
from app.config.settings import DEFAULT_RATES
from app.database.db import get_collection
from app.utils.emi_calculator import calculate_emi, generate_schedule_per_month
from datetime import date, datetime
from bson import ObjectId
from app.exceptions.custom_exceptions import LoanAlreadyStatus, LoanNotFound, InvalidLoanOperation
from app.log.logger import get_logger
from app.utils.decorators import log_execution_time
from app.database.db import admin_col, borrower_col

logger = get_logger("loan_repayments_col")

loans_col = get_collection("loans")
repayments_col = get_collection("repayments")

@log_execution_time
async def apply_loan(payload: dict) -> dict:
    # -------- check role ------------
    if payload.get("role") in "BORROWER":

        # Prevent multiple loans of the same type unless closed/rejected
        active_loan = await loans_col.find_one(
            {
                "customer_id": payload["customer_id"],
                "loan_type": payload["loan_type"],
                "status": {"$nin": ["CLOSED", "REJECTED"]},
            }
        )

        if active_loan:
            raise HTTPException(
                status_code=400,
                detail=f"You already have an active {payload['loan_type']} loan. "
                    f"Please close it before applying for another {payload['loan_type']} loan."
            )
      
        loan_type = payload.get("loan_type")
        annual_rate = payload.get("annual_rate") or DEFAULT_RATES.get(loan_type, 9.0)

        # ---------------- Safe start_date handling ----------------
        start_date = payload.get("start_date")
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        else:
            start_date = date.today()

        # ---------------- EMI & amortization ----------------
        emi = calculate_emi(payload["principal"], annual_rate, payload["tenure_months"])
        schedule = generate_schedule_per_month(payload["principal"], annual_rate, payload["tenure_months"], start_date)
        
        # ---------------- Prepare loan document ----------------
        doc = {
            "customer_id": payload["customer_id"],
            "loan_type": loan_type,
            "principal": float(payload["principal"]),
            "annual_rate": float(annual_rate),
            "tenure_months": int(payload["tenure_months"]),
            "status": "APPLIED",
            "applied_at": datetime.utcnow(),
            "emi_amount": emi,
            "remaining_balance": float(payload["principal"]),
            "emi_schedule": schedule,
        }

        # ---------------- Insert into MongoDB ----------------
        res = await loans_col.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc
    else:
        raise HTTPException(status_code=403, detail="Only BORROWER can apply for loans")

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
async def disburse_loan(loan_id: str):
    doc = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not doc:
        raise LoanNotFound(loan_id)
    
    if doc["status"] != "APPROVED":
        if doc["status"] == "DISBURSED":
            raise LoanAlreadyStatus(f"Loan {loan_id} is already DISBURSED")
        if doc["status"] == "REJECTED":
            raise LoanAlreadyStatus(f"Loan {loan_id} is REJECTED and cannot be disbursed")
        raise InvalidLoanOperation("Only APPROVED loans can be disbursed")

    await loans_col.update_one({"_id": doc["_id"]}, {"$set": {"status": "DISBURSED", "disbursed_at": datetime.utcnow()}})
    await get_loan(loan_id)
    
    return {"message": f"Successfully loan DISBURSE with id : {loan_id}"}

@log_execution_time
async def record_repayment(loan_id: str, amount: float, paid_on: datetime = None):
    paid_on = paid_on or datetime.utcnow()
    loan = await loans_col.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise LoanNotFound(loan_id)
    if loan["status"] in ["CLOSED"]:
        raise LoanAlreadyStatus(f"Loan {loan_id} is CLOSED") # type: ignore
    if loan["status"] not in ("DISBURSED",):
        raise InvalidLoanOperation("Only DISBURSED loans accept repayments")
    outstanding = float(loan.get("remaining_balance", 0.0))
    payment = round(float(amount), 2)
    new_outstanding = max(0.0, round(outstanding - payment, 2))
    rep = {"loan_id": loan["_id"], "amount": payment, "paid_on": paid_on, "remaining_balance": new_outstanding}
    await repayments_col.insert_one(rep)
    await loans_col.update_one({"_id": loan["_id"]}, {"$set": {"remaining_balance": new_outstanding}})
    if new_outstanding == 0.0:
        await loans_col.update_one({"_id": loan["_id"]}, {"$set": {"status": "CLOSED", "closed_at": datetime.utcnow()}})
        logger.info(f"Loan {loan["_id"]} is Closed , outstanding is {new_outstanding} ")
    logger.info(f"Loan {loan["_id"]} paid : {payment} and remaining_balance : {new_outstanding}")
    return {"loan_id": loan_id, "paid": payment, "remaining_balance": new_outstanding}



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

@log_execution_time
async def get_all_applied_loans():
    cursor = loans_col.find({"status": "APPLIED"})
    loans = []

    async for doc in cursor:
        # Fetch user details
        user = await borrower_col.find_one({"_id": ObjectId(doc["customer_id"])})

        loan = {
            "id": str(user["_id"]),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() ,
            "email": user.get("email") if user else None,
            "aadhar_number": user.get("aadhar_number") ,
            "role":user.get("role"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "principal": doc.get("principal"),
                "annual_rate": doc.get("annual_rate"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "status": doc.get("status"),
                "applied_at": doc.get("applied_at"),
                "remaining_balance": doc.get("remaining_balance")}
            }
        loans.append(loan)
    return loans

@log_execution_time
async def get_all_approved_loans():
    cursor = loans_col.find({"status": "APPROVED"})
    loans = []

    async for doc in cursor:
        # Fetch user details
        user = await borrower_col.find_one({"_id": ObjectId(doc["customer_id"])})

        loan = {
            "id": str(user["_id"]),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() ,
            "email": user.get("email") if user else None ,
            "aadhar_number": user.get("aadhar_number") ,
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "status": doc.get("status"),
                "approved_by":doc.get("approved_by_admin")
            }
        }
        loans.append(loan)

    return loans

@log_execution_time
async def get_all_disbursed_loans():
    cursor = loans_col.find({"status": "DISBURSED"})
    loans = []

    async for doc in cursor:
        # Fetch user details
        user = await borrower_col.find_one({"_id": ObjectId(doc["customer_id"])})

        loan = {
            "id": str(user["_id"]),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() ,
            "email": user.get("email") if user else None ,
            "aadhar_number": user.get("aadhar_number") ,
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "status": doc.get("status")
            }
        }
        loans.append(loan)

    return loans

@log_execution_time
async def get_all_closed_loans():
    cursor = loans_col.find({"status": "CLOSED"})
    loans = []

    async for doc in cursor:
        # Fetch user details
        user = await borrower_col.find_one({"_id": ObjectId(doc["customer_id"])})

        loan = {
            "id": str(user["_id"]),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() ,
            "email": user.get("email") if user else None,
            "aadhar_number": user.get("aadhar_number"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "status": doc.get("status"),
                }
            
        }

        loans.append(loan)
    return loans

@log_execution_time
async def get_all_rejected_loans():
    cursor = loans_col.find({"status": "REJECTED"})
    loans = []

    async for doc in cursor:
        # Fetch user details
        user = await borrower_col.find_one({"_id": ObjectId(doc["customer_id"])})

        loan = {
            "id": str(user["_id"]),
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() ,
            "email": user.get("email") if user else None ,
            "aadhar_number": user.get("aadhar_number") ,
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "status": doc.get("status"),
                "rejected_by":doc.get("rejected_by_admin"),
                "reason":doc.get("rejection_reason")
            }
        }
        loans.append(loan)

    return loans
