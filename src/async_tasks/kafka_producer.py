import json
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9093"})


player_id = 1


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for message {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def start_trip_event():
    event = {
        "event_type": "start_trip",
        "player_id": "player",
        "ship_id": "ship_id",
        "payload": {"destination": "destination"},
    }

    producer.produce(
        topic="game-events",
        key=str(player_id),
        value=json.dumps(event),
        callback=delivery_report,
    )
    producer.flush()


if __name__ == "__main__":
    start_trip_event()
