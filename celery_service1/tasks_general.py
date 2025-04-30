from celery_service1.utils.celery_config import celery_app
from celery_service1.rag import retrieve_and_generate_response
from celery_service1.logger import logger  

@celery_app.task
def rag_task(query: str):
    logger.info(f"[RAG TASK] Received query: {query}")
    response = retrieve_and_generate_response(query)
    logger.info(f"[RAG TASK] Generated response: {response}")
    return response

@celery_app.task
def interface_task(input_data: str):
    logger.info(f"[INTERFACE TASK] Received data: {input_data}")
    result = f"Interface Processed: {input_data}"
    logger.info(f"[INTERFACE TASK] Processed result: {result}")
    return result

@celery_app.task
def image_generation_task(prompt: str):
    logger.info(f"[IMAGE GEN TASK] Received prompt: {prompt}")
    result = f"Generated image for: {prompt}"
    logger.info(f"[IMAGE GEN TASK] Generated result: {result}")
    return result
