# src/test_db.py

import asyncio
from src.async_tasks.kafka_consumer import consume_event
from src.utils.logger import logger

if __name__ == "__main__":
    logger.info("Application started.")
    asyncio.run(consume_event())
