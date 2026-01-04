from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from typing_extensions import TypedDict

from pymongo import MongoClient
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver

from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_groq import ChatGroq

from ai_chatbot.app.config.settings import (
    GOOGLE_API_KEY,
    MONGO_URI,
    DB_NAME,
    GROQ_API_KEY
)
from ai_chatbot.app.vector_store.chroma_store import get_chroma_retriever


# ============================================================
# STATE (MUST be TypedDict)
# ============================================================
class RAGState(TypedDict):
    query: str
    customer_data: str
    retrieved_docs: List[str]
    answer: str
    chat_history: List[Dict[str, str]]


# ============================================================
# CHECKPOINTER
# ============================================================
def get_mongo_checkpointer():
    client = MongoClient(MONGO_URI)
    return MongoDBSaver(
        client=client,
        db_name=DB_NAME,
        collection_name="conversation_memory"
    )


# ============================================================
# RETRIEVER TOOL
# ============================================================
async def retrieve_tool(query: str) -> str:
    retriever = get_chroma_retriever()
    if not retriever:
        return "No loan policies available."

    docs = await retriever.ainvoke(query)
    return "\n\n".join(d.page_content for d in docs)


loan_policy_tool = Tool(
    name="loan_policy_retriever",
    func=retrieve_tool,
    coroutine=retrieve_tool,
    description="Retrieve bank loan rules"
)


# ============================================================
# ROUTER NODE
# ============================================================
async def router_node(state: RAGState) -> RAGState:
    state.setdefault("chat_history", [])
    state.setdefault("customer_data", "Anonymous user")
    state.setdefault("retrieved_docs", [])
    state.setdefault("answer", "")
    return state


# ============================================================
# RETRIEVAL NODE
# ============================================================
async def retrieval_node(state: RAGState) -> RAGState:
    docs = await loan_policy_tool.ainvoke(state["query"])
    state["retrieved_docs"] = [docs]
    return state


# ============================================================
# GENERATION NODE
# ============================================================
async def generate_answer_node(state: RAGState) -> RAGState:
    history_text = ""
    for turn in state["chat_history"]:
        history_text += (
            f"Customer: {turn['user']}\n"
            f"Assistant: {turn['assistant']}\n\n"
        )

    docs_text = "\n\n".join(state["retrieved_docs"]) or "No policies found."

    prompt = PromptTemplate(
    input_variables=["history", "customer", "docs", "query"],
    template="""
                You are a professional Bank Loan Officer assisting a customer.

                Your personality:
                - Confident
                - Clear
                - Decisive
                - Helpful

                Conversation History:
                {history}

                Customer Profile:
                {customer}

                Applicable Loan Policies:
                {docs}

                Customer Question:
                {query}

                Response Rules (VERY IMPORTANT):
                1. Answer directly. No introductions.
                2. Never apologize unless a real system error happened.
                3. Never say “based on policy” or “according to documents”.
                4. State eligibility, limits, or restrictions clearly.
                5. If something is missing:
                - Ask only for the missing detail
                - Explain why it is needed in one sentence
                6. If something is not allowed:
                - Say it clearly
                - Give one short reason
                7. Use confident, human language.
                8. Do NOT mention internal rules, AI, or system behavior.

                Write the final answer now.
                """
         )
    
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
        temperature=0
    )

    result = await llm.ainvoke(
        prompt.format(
            history=history_text,
            customer=state["customer_data"],
            docs=docs_text,
            query=state["query"]
        )
    )

    # 🔥 MEMORY WRITE
    state["chat_history"].append({
        "user": state["query"],
        "assistant": result.content
    })

    state["answer"] = result.content
    return state


# ============================================================
# BUILD GRAPH
# ============================================================
def build_rag_graph():
    graph = StateGraph(RAGState)

    graph.add_node("router", router_node)
    graph.add_node("retrieve", retrieval_node)
    graph.add_node("generate", generate_answer_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile(
        checkpointer=get_mongo_checkpointer()
    )
