from fastapi import APIRouter, HTTPException, status
from console_code.app.models.loan_schema import LoanApplyRequest, LoanResponse, RejectRequest
from console_code.app.services.loan_service import apply_loan, approve_loan, disburse_loan, record_repayment, reject_loan
from console_code.app.exceptions.custom_exceptions import LoanAlreadyStatus, LoanNotFound, InvalidLoanOperation
from console_code.app.log.logger import get_logger
from fastapi import Depends
from console_code.app.utils.decorators import get_current_user, require_role
from console_code.app.database.db import loans_col

logger = get_logger("loan")

router = APIRouter(prefix="/loans", tags=["loans"])

@router.post("/apply", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def apply_endpoint(payload: LoanApplyRequest, current = Depends(get_current_user)):
    try:
        # merge JWT user id into payload dict
        data = payload.dict()
        # Extract user document
        user_doc = current.get("user")
        role = current.get("role")

        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid token: missing user data")

        # Inject customer_id and role
        data["customer_id"] = str(user_doc["_id"])
        data["role"] = role   

        # call apply_loan with one dict argument
        doc = await apply_loan(data)

        doc["id"] = str(doc["_id"])
        logger.info(f"Successfully loan applied : {doc['id']}")

        return LoanResponse(
            id=doc["id"],
            customer_id=str(doc["customer_id"]),
            loan_type=doc["loan_type"],
            principal=doc["principal"],
            annual_rate=doc["annual_rate"],
            tenure_months=doc["tenure_months"],
            emi_amount=doc["emi_amount"],
            status=doc["status"],
            applied_at=doc["applied_at"],
            remaining_balance=doc["remaining_balance"],
            emi_schedule=doc.get("emi_schedule")
        )
    except Exception as e:
        logger.exception(f"Error applying loan : {str(e)}")
        raise e
    
@router.post("/{loan_id}/approve")
async def approve_endpoint(loan_id: str, current = Depends(require_role("ADMIN")) ):
    try:
        # Ensure only ADMIN can reject
        if current.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Only ADMIN can approve loans")

        admin_doc = current.get("user")
        if not admin_doc:
            raise HTTPException(status_code=401, detail="Invalid token: missing admin data")

        admin_id = str(admin_doc["_id"])
        logger.info(f"Loan id {loan_id} approved by {admin_id}")
        return await approve_loan(loan_id, admin_id)
    except (LoanNotFound, InvalidLoanOperation,LoanAlreadyStatus) as e:
        logger.warning(f"loan approve warning : {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error approving loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{loan_id}/disburse")
async def disburse_endpoint(
    loan_id: str,
    current=Depends(require_role("ADMIN"))
):
    try:
        # Role check
        if current.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Only ADMIN can disburse loans")

        admin_doc = current.get("user")
        if not admin_doc:
            raise HTTPException(status_code=401, detail="Invalid token: missing admin data")

        admin_id = str(admin_doc["_id"])

        logger.info(f"Loan id {loan_id} disbursed by admin {admin_id}")

        return await disburse_loan(loan_id, admin_id)

    except (LoanNotFound, InvalidLoanOperation, LoanAlreadyStatus) as e:
        logger.warning(f"loan disburse warning : {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error disbursing loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# @router.get("/repayments/eligible")
# async def get_disbursed_loans(current=Depends(get_current_user)):
#     user = current.get("user")
#     role = current.get("role")

#     logger.info(f"Repayment check for role={role}, user={user['_id']}")

#     if role != "BORROWER":
#         raise HTTPException(status_code=403, detail="Only borrowers allowed")

#     customer_id = str(user["_id"])

#     cursor = loans_col.find({
#         "customer_id": customer_id,
#         "status": "DISBURSED"
#     })

#     loans = await cursor.to_list(length=None)

#     logger.info(f"Found {len(loans)} disbursed loans")

#     return [
#         {
#             "id": str(l["_id"]),
#             "loan_type": l["loan_type"],
#             "emi_amount": l["emi_amount"],
#             "remaining_balance": l["remaining_balance"],
#             "status": l["status"]
#         }
#         for l in loans
#     ]

@router.post("/{loan_id}/repay")
async def repay_endpoint(
    loan_id: str,
    amount: float,
    current=Depends(require_role("BORROWER"))
):
    try:
        user = current.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        customer_id = str(user["_id"])

        return await record_repayment(
            loan_id=loan_id,
            amount=amount,
            customer_id=customer_id
        )

    except (LoanNotFound, InvalidLoanOperation, LoanAlreadyStatus) as e:
        logger.warning(f"Loan repayment warning: {str(e)}")
        raise e

    except Exception as e:
        logger.exception(f"Error paying loan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    
@router.post("/{loan_id}/reject")
async def reject_endpoint(
    loan_id: str,
    body: RejectRequest,   
    current = Depends(require_role("ADMIN"))):
    try:
        # Ensure only ADMIN can reject
        if current.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Only ADMIN can reject loans")

        admin_doc = current.get("user")
        if not admin_doc:
            raise HTTPException(status_code=401, detail="Invalid token: missing admin data")

        admin_id = str(admin_doc["_id"])
        
        logger.info(f"Loan {loan_id} rejected by {admin_id}")
        return await reject_loan(loan_id, admin_id, reason=body.reason)

    except (LoanNotFound, InvalidLoanOperation, LoanAlreadyStatus) as e:
        logger.warning(f"loan rejected warning : {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error rejecting loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

    
@router.get("/my-loans")
async def get_my_loans(current=Depends(get_current_user)):
    user = current.get("user")
    role = current.get("role")

    if role != "BORROWER":
        raise HTTPException(status_code=403, detail="Only borrowers can view their loans")

    customer_id = str(user["_id"])

    cursor = loans_col.find(
        {"customer_id": customer_id}
    ).sort("applied_at", -1)

    loans = []

    async for loan in cursor:
        loans.append({
            "id": str(loan["_id"]),
            "loan_type": loan.get("loan_type"),
            "principal": loan.get("principal"),
            "annual_rate": loan.get("annual_rate"),
            "tenure_months": loan.get("tenure_months"),
            "emi_amount": loan.get("emi_amount"),
            "total_payable": loan.get("total_payable"),             
            "status": loan.get("status"),
            "remaining_balance": loan.get("remaining_balance"),
            "rejection_reason": loan.get("rejection_reason"),        
            "applied_at": loan.get("applied_at"),
        })

    return loans
