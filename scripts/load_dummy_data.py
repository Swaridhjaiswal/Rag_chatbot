import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.vectorstore import create_index, add_document

# Creating index with embedding dimension 384
create_index(384)

# Add dummy documents to Redis
add_document(1, "Redis is an in-memory data structure Store.")
add_document(2, "RAG combines retrieval and generation for better LLM answers.")
add_document(3, "FastAPI is a high-performance Python web framework.")

print("DUMMY Data added to Redis")
