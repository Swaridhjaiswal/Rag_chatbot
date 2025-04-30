import redis 
import numpy as np
from sentence_transformers import SentenceTransformer
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


#local Embedding model
def initialize_embedding_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#redis connection
r = redis.Redis(host= 'localhost', port= 6379, decode_responses= False)

#Name of index
INDEX_NAME= "docs_idx"

#creating index for vector similarity search
def create_index(vector_dim):
    try:
        r.ft(INDEX_NAME).info()
        print(f"Index '{INDEX_NAME}' already exists")
    except:
        schema = [
            VectorField(
                "embedding",
                "FLAT", {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dim,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 1000,
                    "BLOCK_SIZE": 100
                }
            ), TextField("text")
        ]
        r.ft(INDEX_NAME).create_index(
            fields = schema,
            definition=IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH)
            )
        print(f"Created Redis index: {INDEX_NAME}")
        
#Add a Document embedding
def add_document(doc_id, text):
    print(f"Adding document with ID: {doc_id} and Text: {text[:200]}...")  # Debug: Print the text being added
    
    # Check if text is a string
    if not isinstance(text, str):
        print(f"ERROR: Expected text to be a string, but got {type(text)} instead.")
        return

    embedding_model = initialize_embedding_model()
    embedding = embedding_model.encode(text)
    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
    
    r.hset(f"doc:{doc_id}", mapping={
        "embedding": embedding_bytes,
        "text": text.encode('utf-8')  # Ensuring the text is properly encoded as a string
    })
    
#Bulk add multiple chunks from a PDF or large doc    
def add_document_chunks(base_doc_id, chunks):
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i} with text: {chunk[:200]}...")  # Debug: Checking each chunk
        chunk_id = f"{base_doc_id}_chunk_{i}"
        add_document(chunk_id, chunk)

    
#Search for similar docs
def search_similar_docs(query, top_k=3):
    embedding_model = initialize_embedding_model()

    query_embedding = embedding_model.encode(query)
    query_embedding_bytes = np.array(query_embedding, dtype= np.float32).tobytes()
    
    q = f"*=>[KNN {top_k} @embedding $vector AS score]"
    params = {"vector": query_embedding_bytes}
    
    results = r.ft(INDEX_NAME).search(q, query_params=params)
    
    return [doc.text.decode() for doc in results.docs]