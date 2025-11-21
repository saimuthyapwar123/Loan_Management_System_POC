from fastapi import APIRouter, HTTPException, status
from app.models.loan_schema import LoanApplyRequest, LoanResponse, RejectRequest
from app.services.loan_service import apply_loan, approve_loan, disburse_loan, get_all_applied_loans, get_all_approved_loans, get_all_closed_loans, get_all_disbursed_loans, get_all_rejected_loans, record_repayment, reject_loan
from app.exceptions.custom_exceptions import LoanAlreadyStatus, LoanNotFound, InvalidLoanOperation
from app.log.logger import get_logger
from fastapi import Depends
from app.utils.decorators import get_current_user, require_role

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
async def disburse_endpoint(loan_id: str, admin = Depends(require_role("ADMIN"))):
    try:
        logger.info(f"Loan_id {loan_id} is disbursed ")
        return await disburse_loan(loan_id)
    except (LoanNotFound, InvalidLoanOperation,LoanAlreadyStatus) as e:
        logger.warning(f"loan disburse warning : {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error disbursing loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{loan_id}/repay")
async def repay_endpoint(loan_id: str, amount: float,admin = Depends(require_role("BORROWER"))):
    try:
        return await record_repayment(loan_id, amount)
    except (LoanNotFound, InvalidLoanOperation,LoanAlreadyStatus) as e:
        logger.warning(f"loan repayment warning : {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error paying loan : {str(e)}")
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
    
# @router.get("/list_of_applied_loan")
# async def list_applied_loans(admin = Depends(require_role("ADMIN"))):
#     try:
#         loans = await get_all_applied_loans()
#         if not loans:
#             return {"message": "No applied loans found"}
#         logger.info(f"List of applied loan data fetched")
#         return loans
#     except Exception as e:
#         logger.exception(f"Error list_of_applied_loan loan : {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/list_of_approved_loans")
# async def list_approved_loans(admin = Depends(require_role("ADMIN"))):
#     try:
#         loans = await get_all_approved_loans()
#         if not loans:
#             return {"message": "No approved loans found"}
#         logger.info(f"List of approved loan data fetched")
#         return loans
#     except Exception as e:
#         logger.exception(f"Error list_of_approved_loans loan : {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/list_of_disbursed_loans")
# async def list_disbursed_loans(admin = Depends(require_role("ADMIN"))):
#     try:
#         loans = await get_all_disbursed_loans()
#         if not loans:
#             return {"message": "No disbursed loans found"}
#         logger.info(f"List of disbursed loan data fetched")
#         return loans
#     except Exception as e:
#         logger.exception(f"Error list_of_disbursed_loans loan : {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/list_of_closed_loans")
# async def list_closeded_loans(admin = Depends(require_role("ADMIN"))):
#     try:
#         loans = await get_all_closed_loans()
#         if not loans:
#             return {"message": "No closed loans found"}
#         logger.info(f"List of closed loan data fetched")
#         return loans
#     except Exception as e:
#         logger.exception(f"Error list_of_closed_loans loan : {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/list_of_rejected_loans")
# async def list_rejected_loans(admin = Depends(require_role("ADMIN"))):
#     try:
#         loans = await get_all_rejected_loans()
#         if not loans:
#             return {"message": "No rejected loans found"}
#         logger.info(f"List of rejected loan data fetched")
#         return loans
#     except Exception as e:
#         logger.exception(f"Error list_of_rejected_loans loan : {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

