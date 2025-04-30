from celery import Celery 

celery_app = Celery(
    "tasks",
    broker= "redis://localhost:6379/0",
    backend= "redis://localhost:6379/1"
)

celery_app.conf.task_routes = {
    
    "celery_service2.tasks_stream.*": {"queue":"stream"},
    
}