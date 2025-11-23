import google.generativeai as genai
from dotenv import load_dotenv
import os
from app.utils.data_store import retrieve_docs

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def rag_pipeline(user_query: str, customer_data: dict, retrieved_guidelines: list = None, k: int = 3) -> str:
    """
    Perform RAG: retrieve top-k relevant guidelines, include customer data,
    and generate an answer using Gemini.
    """

    # Use provided guidelines if available, otherwise fetch
    if retrieved_guidelines is None:
        retrieved_guidelines = retrieve_docs(user_query, k=k)
    
    context = "\n".join(retrieved_guidelines)

    prompt = f"""
        You are a helpful bank assistant. Use the context below and the customer data
        to answer the user's question accurately.

        Customer Data:
        {customer_data}

        Bank Guidelines Context:
        {context}

        Question:
        {user_query}
        
        ### Instructions:
        1. Detect the language of the customer’s query automatically.  
        2. Respond in the same language.  
        3. Maintain a professional, helpful, and polite tone — like an official bank representative.  
        4. Always base your answer strictly on the given bank guidelines and customer data.  
        5. If any information is missing, politely inform the customer instead of guessing.  
        6. Keep the response short, clear, and human-like.

        Now, generate the best possible reply to the customer.
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"








