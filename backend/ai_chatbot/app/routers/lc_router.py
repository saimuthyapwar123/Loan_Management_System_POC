from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer

from ai_chatbot.app.utils.jwt_handler import decode_access_token
from ai_chatbot.app.models.rag_schema import QueryRequest
from ai_chatbot.app.services.rag_service import rag_with_customer_context
from ai_chatbot.app.database.db import borrower_col, loans_col
from ai_chatbot.app.log.logger import get_logger

router = APIRouter(
    prefix="/Generative_AI_loan_assistant",
    tags=["Generative_AI_loan_assistant"]
)

logger = get_logger("RAG")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/chat", summary="Borrower AI Chat")
async def borrower_chat(
    query: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        if current_user.get("role") != "BORROWER":
            raise HTTPException(status_code=403, detail="Only borrowers allowed")

        borrower_id = current_user.get("user_id") or current_user.get("sub")

        borrower = await borrower_col.find_one(
            {"_id": ObjectId(borrower_id)},
            {"password": 0}
        )

        if borrower is None:
            raise HTTPException(status_code=404, detail="Borrower not found")

        loans = await loans_col.find(
            {"customer_id": str(borrower_id)},
            {"emi_schedule": 0}
        ).to_list(length=50)

        answer = await rag_with_customer_context(
            user_query=query.query,
            borrower=borrower,
            loans=loans
        )
        

        return {"answer": answer}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Borrower RAG failure: {e}")
        raise HTTPException(status_code=500, detail="AI processing failed")
