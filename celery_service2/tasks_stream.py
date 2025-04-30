from celery_service2.utils.celery_config import celery_app
from celery_service2.utils.llm_router import get_llm_response


@celery_app.task
def stream_rag_task(query: str, use_local_llm: bool = True):
    return get_llm_response(query, use_local_llm)

@celery_app.task
def stream_interface_task(data: str, use_local_llm: bool= True):
    return get_llm_response(data, use_local_llm)

@celery_app.task
def stream_image_gen_task(prompt: str):
    return f"[API] Streaming Image generated for: {prompt}"
