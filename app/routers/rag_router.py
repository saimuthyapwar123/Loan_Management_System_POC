from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from app.models.rag_schema import QueryRequest,Query
from app.services.rag_service import rag_pipeline
from app.database.db import borrower_col, loans_col
from app.utils.rag.data_store import retrieve_docs
from app.utils.rag.helper import convert_objectid_to_str
from app.utils.decorators import log_execution_time

router = APIRouter(prefix="/loans_RAG_pipline", tags=["loans_RAG_pipline"])

@log_execution_time
@router.post("/check_customer_id")
async def loan_check(query: QueryRequest):
    try:
        # 1️⃣ Load borrower document by customer_id
        borrower_data = await borrower_col.find_one({"_id": ObjectId(query.customer_id)})
        if not borrower_data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        # 2️⃣ Load all loans for this borrower
        loans_cursor = loans_col.find({"customer_id": str(borrower_data["_id"])})
        loans_list = await loans_cursor.to_list(length=100)
        if not loans_list:
            raise HTTPException(status_code=404, detail="No loans found for this borrower")

        # 3️⃣ Combine and sanitize data
        combined_data = convert_objectid_to_str(borrower_data)
        combined_data["loans"] = [convert_objectid_to_str(loan) for loan in loans_list]

        full_name = f"{combined_data.get('first_name', '')} {combined_data.get('last_name', '')}"

        # 4️⃣ Retrieve relevant bank guidelines using FAISS
        relevant_guidelines = retrieve_docs(query.query, k=query.k)

        # 5️⃣ Generate final answer using RAG pipeline
        final_answer = rag_pipeline(
            user_query=query.query,
            customer_data=combined_data,
            retrieved_guidelines=relevant_guidelines,
            k=query.k
        )

        # 6️⃣ Return response
        return {
            "customer_data": full_name,
            "loans_count": len(loans_list),
            "answer": final_answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





