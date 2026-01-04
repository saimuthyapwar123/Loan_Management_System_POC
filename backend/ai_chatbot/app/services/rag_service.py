from ai_chatbot.app.services.rag_graph import build_rag_graph
from ai_chatbot.app.utils.context_builder import build_customer_context

graph = build_rag_graph()


# --------------------------
# PUBLIC CHAT
# --------------------------
async def rag_doc_only(user_query: str, thread_id: str | None):
    state = {
        "query": user_query,
        "customer_data": "Anonymous user",
        "retrieved_docs": [],
        "answer": ""
   }


    result = await graph.ainvoke(
        state,
        config={
            "configurable": {
                "thread_id": thread_id or "public"
            }
        }
    )

    return result["answer"]


# --------------------------
# AUTHENTICATED CHAT
# --------------------------
async def rag_with_customer_context(user_query: str, borrower: dict, loans: list):
    context = build_customer_context(borrower, loans)

    thread_id = f"user_{borrower['_id']}"

    state = {
        "query": user_query,
        "customer_data": context,
        "retrieved_docs": [],
        "answer": ""
    }

    result = await graph.ainvoke(
        state,
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return result["answer"]
