from ai_chatbot.app.services.rag_graph import build_rag_graph
from ai_chatbot.app.utils.context_builder import build_customer_context

# ✅ One shared graph for both modes
graph = build_rag_graph()


# -------------------------------------------------
# BEFORE LOGIN → Document RAG only
# -------------------------------------------------
async def rag_doc_only(user_query: str) -> str:
    state = {
        "query": user_query,
        "customer_data": "Anonymous user. No personal data available.",
        "retrieved_docs": [],
        "answer": ""
    }

    result = await graph.ainvoke(state)
    return result["answer"]


# -------------------------------------------------
# AFTER LOGIN → Document RAG + MongoDB context
# -------------------------------------------------
async def rag_with_customer_context(
    user_query: str,
    borrower: dict,
    loans: list[dict]
) -> str:
    customer_context = build_customer_context(borrower, loans)

    state = {
        "query": user_query,
        "customer_data": customer_context,
        "retrieved_docs": [],
        "answer": ""
    }

    result = await graph.ainvoke(state)
    return result["answer"]
