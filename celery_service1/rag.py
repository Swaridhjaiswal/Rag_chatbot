from celery_service1.utils.vectorstore import search_similar_docs
from celery_service1.utils.llm_router import get_llm_response
from sentence_transformers import SentenceTransformer

# Load embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_and_generate_response(query: str, use_local_llm: bool = True) -> str:
    """
    RAG process: retrieve relevant documents, build context, and query LLM
    """

    # Step 1: Retrieve top 3 similar documents from vector DB
    docs = search_similar_docs(query, top_k=3)

    # Step 2: Combine retrieved docs into context string
    context = "\n".join(docs)

    # Step 3: Build final prompt for LLM
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    # Step 4: Pass prompt to selected LLM (local or API)
    response = get_llm_response(prompt, use_local_llm)

    return response
