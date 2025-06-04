import json
import asyncio
from confluent_kafka import Consumer, KafkaError
from src.events.handlers import handle_travel_event
from src.utils.logger import logger

consumer = Consumer(
    {
        "bootstrap.servers": "localhost:9093",
        "group.id": "game-event-consumer",
        "auto.offset.reset": "earliest",
    }
)


async def consume_event():
    consumer.subscribe(["game-events"])
    logger.info("kafka consumer started waiting for events")

    loop = asyncio.get_event_loop()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(0.1)
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break
        event = json.loads(msg.value().decode("utf-8"))
        event_type = event.get("event_type")

        if event_type == "start_trip":
            loop.create_task(handle_travel_event(event))
        else:
            print(f"Unknown event type: {event_type}")

    consumer.close()
