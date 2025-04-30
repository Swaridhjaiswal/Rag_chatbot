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

#Search the similar docs        
def search_similar_docs(query, top_k=3):
    embedding_model = initialize_embedding_model()
    query_embedding = embedding_model.encode(query)
    
    # Convert the query embedding to bytes (ensure it's float32)
    query_embedding_bytes = np.array(query_embedding, dtype=np.float32).tobytes()
    
    # Correct KNN query structure
    q = f"*=>[KNN {top_k} @embedding $vector AS score]"
    
    # Redis search parameters
    params = {
        "vector": query_embedding_bytes
    }
    
    try:
        # Perform the search
        results = r.ft(INDEX_NAME).search(q, query_params=params)
        
        # Return the results (decode text from byte format)
        return [doc.text.decode() for doc in results.docs]
    except redis.exceptions.ResponseError as e:
        print(f"Redis Error: {e}")
        return []
