from fastapi import APIRouter, HTTPException
from ai_chatbot.app.models.rag_schema import QueryRequest
from ai_chatbot.app.services.rag_service import rag_doc_only
from ai_chatbot.app.log.logger import get_logger

router = APIRouter(
    prefix="/chat",
    tags=["AI Chatbot"]
)

logger = get_logger("PUBLIC_RAG")


@router.post("/query", summary="Public AI Chat (Document RAG only)")
async def chat_query(request: QueryRequest):
    """
    Handles chatbot queries BEFORE login.
    Uses only policy documents (PDF RAG).
    """

    try:
        answer = await rag_doc_only(
            user_query=request.query
        )

        return {
            "success": True,
            "answer": answer
        }

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )

    except Exception as e:
        logger.exception("Public chatbot failure")
        raise HTTPException(
            status_code=500,
            detail="AI service failed. Please try again later."
        )
