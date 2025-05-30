import json
from confluent_kafka import Producer
import hashlib

producer = Producer({"bootstrap.servers": "localhost:9093"})


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for message {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def start_trip_event(player_token, destination_waypoint, shipsymbol):
    event = {
        "event_type": "start_trip",
        "destination_waypoint": destination_waypoint,
        "player_token": player_token,
        "ship_symbol": shipsymbol,
    }

    producer.produce(
        topic="game-events",
        key=hashlib.sha256(player_token.encode()).hexdigest(),
        value=json.dumps(event),
        callback=delivery_report,
    )
    producer.flush()
