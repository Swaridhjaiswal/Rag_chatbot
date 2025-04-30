from celery_service1.utils.celery_config import celery_app
import celery_service1.tasks_general  # Import tasks to register them with Celery
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)


# Start the Celery worker with the "general" queue
# Command to run: celery -A celery_service1.tasks_general worker --loglevel=info --queues=general
