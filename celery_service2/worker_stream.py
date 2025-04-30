import multiprocessing
multiprocessing.set_start_method('spawn', force=True)

from celery_service2.utils.celery_config import celery_app
import celery_service2.tasks_stream
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# celery -A celery_service2.tasks_stream worker --loglevel=info --queues=stream
