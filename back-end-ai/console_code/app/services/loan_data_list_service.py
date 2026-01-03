from console_code.app.database.db import loans_col,borrower_col
from bson import ObjectId
from console_code.app.log.logger import get_logger
from console_code.app.utils.decorators import log_execution_time

logger = get_logger("loan_repayments_col")


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
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "annual_rate": doc.get("annual_rate"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
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
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
                "remaining_balance": doc.get("remaining_balance"),
                "status": doc.get("status"),
                "approved_by": doc.get("approved_by_admin"),
                "approved_at": doc.get("approved_at"),
            }
        }
        loans.append(loan)

    return loans

# @log_execution_time
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
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
                "status": doc.get("status"),
                "remaining_balance": doc.get("remaining_balance"),
                "approved_by": doc.get("approved_by_admin"),
                "approved_at": doc.get("approved_at"),
            }
        }
        loans.append(loan)

    return loans

# @log_execution_time
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
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),
            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
                "status": doc.get("status"),
                "remaining_balance": doc.get("remaining_balance"),
                "approved_by": doc.get("approved_by_admin"),
                "approved_at": doc.get("approved_at"),
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
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),

            "loan":{
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
                "status": doc.get("status"),
                "remaining_balance": doc.get("remaining_balance"),
                "rejected_by":doc.get("rejected_by_admin"),
                "reason":doc.get("rejection_reason")
            }
        }
        loans.append(loan)

    return loans


@log_execution_time
async def get_loans_by_status(status: str | None = None):
    """
    status:
      - None or 'ALL' → return all loans
      - APPLIED / APPROVED / DISBURSED / REJECTED / CLOSED
    """

    query = {}
    if status and status != "ALL":
        query["status"] = status

    cursor = loans_col.find(query)
    loans = []

    async for doc in cursor:
        user = await borrower_col.find_one(
            {"_id": ObjectId(doc["customer_id"])}
        )

        loans.append({
            "id": str(user["_id"]) if user else None,
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else "N/A",
            "email": user.get("email") if user else None,
            "aadhar_number": user.get("aadhar_number") if user else None,
            "pan_number": user.get("pan_number"),
            "dob": user.get("dob"),
            "address": user.get("address"),
            "loan": {
                "id": str(doc["_id"]),
                "customer_id": str(doc["customer_id"]),
                "loan_type": doc.get("loan_type"),
                "credit_score": doc.get("credit_score"),
                "principal": doc.get("principal"),
                "tenure_months": doc.get("tenure_months"),
                "emi_amount": doc.get("emi_amount"),
                "total_payable": doc.get("total_payable"),
                "status": doc.get("status"),
                "remaining_balance": doc.get("remaining_balance"),
                "applied_at": doc.get("applied_at"),
                "approved_by": doc.get("approved_by_admin"),
                "rejected_by": doc.get("rejected_by_admin"),
                "rejection_reason": doc.get("rejection_reason"),
            }
        })

    return loans

