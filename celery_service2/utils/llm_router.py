import os
from celery_service2.utils.vectorstore import search_similar_docs
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# Load .env relative to celerytwo/
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# Set Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_local_llm(query: str) -> str:
    # Dummy local LLM call
    return f"[local LLM] Answer to: {query}"

def call_api_llm(query: str) -> str:
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(
        query,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 500
        }
    )
    return response.text.strip()

def get_llm_response(query: str, use_local: bool = True) -> str:
    # Step 1: Retrieve relevant chunks from vectorstore
    retrieved_docs = search_similar_docs(query)
    context = "\n".join(retrieved_docs)
    
    # Step 2: Format the prompt
    full_prompt = f"Use the following context to answer the query:\n\n{context}\n\nQuery: {query}"
    
    # Step 3: Call LLM with the context
    if use_local:
        return call_local_llm(full_prompt)
    return call_api_llm(full_prompt)
