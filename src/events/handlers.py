import asyncio
from datetime import datetime
from src.utils.logger import logger
from src.db.models import ShipNavigation, Ship
from src.db.db_session import get_session
from src.objects.player import Player
from src.objects.ship import SpaceShip


async def handle_travel_event(event):
    player_token = event["player_token"]
    destination_waypoint = event["destination_waypoint"]
    ship_symbol = event["ship_symbol"]
    player = Player(player_token)
    ship = SpaceShip.load_or_create(player=player, shipSymbol=ship_symbol)
    distance = ship.db.get_distance_to_waypoint(
        destination_waypoint=destination_waypoint
    )
    logger.info(
        f"ship is at {ship.waypointSymbol} and going to {destination_waypoint} at distance {distance}"
    )
    if ship.waypointSymbol == destination_waypoint:
        logger.info("You are already at that location")
        return
    if ship.status == "DOCKED":
        logger.info("Going to Orbit")
        ship.api.get_in_orbit()
        ship.status = "IN_ORBIT"
        ship.save_to_db(
            update_all_subcomponents=False, update_modules=False, update_mounts=False
        )
        ship.telemetry.update_ShipNavigation()

    if ship.status == "IN_TRANSIT":
        logger.info(
            "Ship is already in transit. Please wait until the current travel is complete."
        )
        return

    ##api call
    logger.info(f"Initiating travel to {destination_waypoint}...")
    response = ship.api.travel_to_waypoint(destination_waypoint)
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
    logger.info(f"ship status during trip is {ship.status}")
    await asyncio.sleep(travel_duration)
    ship.update_from_api()
    ship.save_to_db()
    logger.info(f"{ship.shipSymbol} is now in {ship.status}")
    logger.info(f"{ship.shipSymbol} has reached {ship.waypointSymbol}")


async def handle_extract_event(event):
    player_token = event["player_token"]
    ship_symbol = event["ship_symbol"]
    player = Player(player_token)
    ship = SpaceShip.load_or_create(player=player, shipSymbol=ship_symbol)

    if ship.status == "DOCKED":
        logger.info("Going to Orbit")
        ship.api.get_in_orbit()
        ship.status = "IN_ORBIT"
        ship.save_to_db(
            update_all_subcomponents=False, update_modules=False, update_mounts=False
        )
        ship.telemetry.update_ShipNavigation()

    if ship.status == "IN_TRANSIT":
        logger.info(
            "Ship is in transit. Please wait until the current travel is complete."
        )
        return
    cargo = ship.db.fetch_shipcargo_from_db()
    current_capacity = cargo.get("current_capacity", 0)
    max_capacity = cargo.get("Total_capacity", 0)
    if current_capacity >= max_capacity:
        logger.info(
            f"Ship cargo is full. Current capacity: {current_capacity}, Max capacity: {max_capacity}"
        )
        return
    logger.info("Preparing laser for extraction...")
    extract_json = ship.resource_operations.extract()
    if not extract_json or "error" in extract_json:
        logger.error("Extraction failed. Please check the ship's status and resources.")
        return
    ship.save_to_db()
    logger.info("Extraction complete!")
    cooldown_time = extract_json.get("data").get("cooldown").get("totalSeconds")
    logger.info(
        f"Extraction cooldown time: {cooldown_time} seconds , waiting for laser to cool down..."
    )
    await asyncio.sleep(cooldown_time)
    ship.telemetry.update_ShipCooldown()
    logger.info("Laser is ready for the next extraction.")
