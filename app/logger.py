import logging

logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
