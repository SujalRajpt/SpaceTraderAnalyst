import asyncio
from datetime import datetime
from src.utils import logger
from src.db.models import ShipNavigation, Ship
from src.db.db_session import get_session
from src.utils.logger import logger
from src.objects.player import Player
from src.objects.ship import SpaceShip


async def handle_travel_event(event):
    player_token = event["player_token"]
    destination_waypoint = event["destination_waypoint"]
    ship_symbol = event["ship_symbol"]

    player = Player(agent_token=player_token)
    ship = SpaceShip.load_or_create(player=player, shipSymbol=ship_symbol)
    if ship.waypointSymbol == destination_waypoint:
        logger.info("You are already at that location")
        return
    if ship.status == "DOCKED":
        logger.info("Going to Orbit")
        ship.get_in_orbit()
    if ship.status == "IN_TRANSIT":
        logger.info(
            "Ship is already in transit. Please wait until the current travel is complete."
        )
        return

    ship.save_to_db()

    ##api call
    logger.info(f"Initiating travel to {destination_waypoint}...")
    response = ship.travel_to_waypoint(destination_waypoint)
    if response:
        ship.status = "IN_TRANSIT"

    logger.info("Event received in handler")

    arrival_time = (
        response.get("data", {}).get("nav", {}).get("route", {}).get("arrival")
    )
    departure_time = (
        response.get("data", {}).get("nav", {}).get("route", {}).get("departureTime")
    )
    arrival_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))
    departure_dt = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))
    travel_duration = (arrival_dt - departure_dt).total_seconds()

    with get_session() as session:
        ship_db = session.query(Ship).filter(Ship.symbol == ship.shipSymbol).first()
        shipnav = (
            session.query(ShipNavigation)
            .filter(ShipNavigation.ship_id == ship_db.id)
            .first()
        )
        shipnav.arrival_time = arrival_time
        shipnav.departure_time = departure_time
        shipnav.destination_system = (
            response.get("data", {}).get("nav", {}).get("systemSymbol", {})
        )
        shipnav.destination_waypoint = (
            response.get("data", {}).get("nav", {}).get("waypointSymbol", {})
        )
        session.commit()

    logger.info(f"Sleeping for {travel_duration} seconds to simulate travel...")
    print(f"ship status during trip is {ship.status}")
    await asyncio.sleep(travel_duration)
    ship.update_from_api()
    ship.save_to_db()
    print(f"ship status after trip is {ship.status}")
    logger.info(f"{ship.shipSymbol} has reached {ship.waypointSymbol}")
