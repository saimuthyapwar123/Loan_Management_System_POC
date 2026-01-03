from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool

from ai_chatbot.app.vector_store.chroma_store import get_chroma_retriever

from ai_chatbot.app.config.settings import GOOGLE_API_KEY,GROQ_API_KEY


# --------------------------
# State
# --------------------------
class RAGState(dict):
    query: str
    customer_data: dict
    retrieved_docs: list
    answer: str


# --------------------------
# ASYNC Tool: Retriever
# --------------------------
async def retrieve_tool(query: str):
    retriever = get_chroma_retriever()
    if retriever is None:
        return "No policy documents available."

    docs = await retriever.ainvoke(query)
    return "\n\n".join(d.page_content for d in docs)


loan_policy_tool = Tool(
    name="loan_policy_retriever",
    func=retrieve_tool,
    coroutine=retrieve_tool,
    description="Retrieve relevant bank loan guidelines."
)


# --------------------------
# Node 1: FORCE retrieval
# --------------------------
async def router_node(state: RAGState):
    # ✅ Always retrieve documents for logged-in users
    state["retrieved_docs"] = []
    return state


# --------------------------
# Node 2: Retrieve docs
# --------------------------
async def retrieval_node(state: RAGState):
    retrieved_text = await loan_policy_tool.ainvoke(state["query"])
    state["retrieved_docs"] = [retrieved_text]
    return state


# --------------------------
# Node 3: Generate Answer
# --------------------------
async def generate_answer_node(state: RAGState):

    docs_text = (
        "\n\n".join(state["retrieved_docs"])
        if state["retrieved_docs"]
        else "No policies retrieved."
    )

    prompt = PromptTemplate(
        input_variables=["customer", "docs", "query"],
        template="""
           You are a Bank Loan Assistant chatting with a customer.

            Your behavior:
            - Answer questions clearly, confidently, and professionally.
            - Speak like a helpful bank representative, not like a disclaimer bot.
            - Your answers should make the customer feel satisfied and informed.

            Conversation Context:
            Customer Details:
            {customer}

            Bank Loan Rules:
            {docs}

            Customer Question:
            {query}

            Strict Chat Rules:
            1. Answer the customer’s question directly whenever possible.
            2. Do NOT start responses with apologies unless an error truly occurred.
            3. Do NOT give vague or generic answers.
            4. If the answer exists in bank rules, state it clearly.
            5. If information is missing:
            - Ask for ONLY the exact missing detail.
            - Explain briefly WHY it is needed.
            6. If the request is not allowed:
            - Clearly say it is not allowed.
            - Give a short, understandable reason.
            7. Keep responses short, confident, and conversational.
            8. Never mention internal policies, reasoning steps, or limitations.

            Tone Guidelines:
            - Confident
            - Helpful
            - Human-like
            - Clear and polite

            Final Answer:


        """
    )

    # llm = ChatGroq(
    #     model="llama-3.1-8b-instant",
    #     api_key=GROQ_API_KEY,
    #     temperature=0
    # )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    result = await llm.ainvoke(
        prompt.format(
            customer=state["customer_data"],
            docs=docs_text,
            query=state["query"]
        )
    )

    state["answer"] = result.content
    return state


# --------------------------
# Build Graph
# --------------------------
def build_rag_graph():
    graph = StateGraph(RAGState)

    graph.add_node("router", router_node)
    graph.add_node("retrieve", retrieval_node)
    graph.add_node("generate", generate_answer_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()
