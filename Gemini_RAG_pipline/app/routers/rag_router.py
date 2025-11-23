from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from app.models.rag_schema import QueryRequest
from app.services.rag_service import rag_pipeline
from app.database.db import borrower_col, loans_col
from app.utils.data_store import retrieve_docs
from app.utils.helper import convert_objectid_to_str
from app.utils.decorators import log_execution_time
from app.log.logger import get_logger
from bson.errors import InvalidId

router = APIRouter(prefix="/loans_RAG_pipeline", tags=["loans_RAG_pipeline"])
logger = get_logger("loans_RAG_pipeline")


@log_execution_time
@router.post("/{borrower_id}")
async def loan_check(query: QueryRequest, borrower_id: str):

    try:
        # Validate ObjectId
        try:
            borrower_obj_id = ObjectId(borrower_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid borrower_id format")

        # 1️⃣ Fetch borrower details using borrower_id
        borrower_data = await borrower_col.find_one({"_id": borrower_obj_id})
        if not borrower_data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        # 2️⃣ Fetch loans using borrower _id as customer_id
        loans_cursor = loans_col.find({"customer_id": str(borrower_data["_id"])})
        loans_list = await loans_cursor.to_list(length=100)

        if not loans_list:
            raise HTTPException(status_code=404, detail="No loans found for this borrower")

        # 3️⃣ Structure and sanitize combined response data
        combined_data = convert_objectid_to_str(borrower_data)
        combined_data["loans"] = [convert_objectid_to_str(loan) for loan in loans_list]

        full_name = f"{combined_data.get('first_name', '')} {combined_data.get('last_name', '')}".strip()

        # 4️⃣ Retrieve relevant documents using vector search
        relevant_guidelines = retrieve_docs(query.query, k=query.k)

        # 5️⃣ Pass everything to RAG pipeline
        final_answer = rag_pipeline(
            user_query=query.query,
            customer_data=combined_data,
            retrieved_guidelines=relevant_guidelines,
            k=query.k
        )

        logger.info(f"Query: {query.query}\nAnswer: {final_answer}")

        # 6️⃣ Return response
        return {
            "customer_name": full_name,
            "answer": final_answer
        }

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
