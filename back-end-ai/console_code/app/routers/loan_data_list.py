from fastapi import APIRouter, HTTPException, status,Query
from console_code.app.services.loan_data_list_service import ( 
    get_all_applied_loans, get_all_approved_loans, get_all_closed_loans, get_all_disbursed_loans, get_all_rejected_loans, 
    get_loans_by_status)
from console_code.app.log.logger import get_logger
from fastapi import Depends
from console_code.app.utils.decorators import require_role

logger = get_logger("loan")

router = APIRouter(prefix="/loans_list", tags=["loans"])

@router.get("/list_of_applied_loan")
async def list_applied_loans(admin = Depends(require_role("ADMIN"))):
    try:
        loans = await get_all_applied_loans()
        if not loans:
            return {"message": "No applied loans found"}
        logger.info(f"List of applied loan data fetched")
        return loans
    except Exception as e:
        logger.exception(f"Error list_of_applied_loan loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/list_of_approved_loans")
async def list_approved_loans(admin = Depends(require_role("ADMIN"))):
    try:
        loans = await get_all_approved_loans()
        if not loans:
            return {"message": "No approved loans found"}
        logger.info(f"List of approved loan data fetched")
        return loans
    except Exception as e:
        logger.exception(f"Error list_of_approved_loans loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/list_of_disbursed_loans")
async def list_disbursed_loans(admin = Depends(require_role("ADMIN"))):
    try:
        loans = await get_all_disbursed_loans()
        if not loans:
            return {"message": "No disbursed loans found"}
        logger.info(f"List of disbursed loan data fetched")
        return loans
    except Exception as e:
        logger.exception(f"Error list_of_disbursed_loans loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/list_of_closed_loans")
async def list_closeded_loans(admin = Depends(require_role("ADMIN"))):
    try:
        loans = await get_all_closed_loans()
        if not loans:
            return {"message": "No closed loans found"}
        logger.info(f"List of closed loan data fetched")
        return loans
    except Exception as e:
        logger.exception(f"Error list_of_closed_loans loan : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list_of_rejected_loans")
async def list_rejected_loans(admin = Depends(require_role("ADMIN"))):
    try:
        loans = await get_all_rejected_loans()
        if not loans:
            return {"message": "No rejected loans found"}
        logger.info(f"List of rejected loan data fetched")
        return loans
    except Exception as e:
        logger.exception(f"Error list_of_rejected_loans loan : {str(e)}")
        raise 



@router.get("/list")
async def list_loans(
    status: str = Query(default="ALL"),
    admin=Depends(require_role("ADMIN"))
):
    """
    Examples:
    /loans/list?status=APPLIED
    /loans/list?status=APPROVED
    /loans/list?status=DISBURSED
    /loans/list?status=REJECTED
    /loans/list?status=CLOSED
    /loans/list?status=ALL
    """

    try:
        loans = await get_loans_by_status(status.upper())
        if not loans:
            return {"message": "No loans found"}

        logger.info(f"Loans fetched with status={status}")
        return loans

    except Exception as e:
        logger.exception("Error fetching loans")
        raise HTTPException(status_code=500, detail=str(e))
