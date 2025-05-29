import asyncio
from datetime import datetime
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.models import Agent
from src.db.db_session import get_session
from src.utils.pretty_print import pretty_print
from src.objects.sol_system import SolSystem
import json


# with get_session() as session:
#     agent = session.query(Agent).filter_by(id=1).first()
#     if agent:
#         agent_token = agent.agent_token
#         symbol = agent.symbol
#     else:
#         agent_token = None


# player = Player(agent_token=agent_token)
# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[1], player=player)
# nav = ship.fetch_navigation_info_from_db()
# origin_system = nav["origin_system"]
# sol = SolSystem(origin_system)
# wps = sol.get_waypoints()
# neighbor_1 = wps[3]["waypoint_symbol"]
# print(ship)


with open("json.txt", "r", encoding="utf-8") as file:
    test_json = json.load(file)


async def handle_travel_event(event, destination_waypoint=0, ship=0):
    # if ship.status == "DOCKED":
    #     ship.get_in_orbit()
    # if ship.status == "IN_TRANSIT":
    #     print(
    #         "Ship is already in transit. Please wait until the current travel is complete."
    #     )
    #     response = ship.travel_to_waypoint(destination_waypoint)
    #     pretty_print(f"Travel response: {response}")
    #     return

    # print(f"Traveling to {destination_waypoint}...")
    # print(
    #     f"The distance to waypoint {destination_waypoint} is {ship.get_distance_to_waypoint(destination_waypoint=destination_waypoint)} units"
    # )
    # print(f"Press 1 to travel to {destination_waypoint} or any other key to cancel.")
    # choice = input("Enter your choice: ")
    # if choice != "1":
    #     print("Travel cancelled.")
    #     return
    # ship.status = "IN_TRANSIT"
    # ship.save_to_db()
    # print(f"Initiating travel to {destination_waypoint}...")
    # response = ship.travel_to_waypoint(destination_waypoint)
    # pretty_print(f"Travel response: {response}")
    print("Event received in handler")
    arrival_time = (
        test_json.get("data", {}).get("nav", {}).get("route", {}).get("arrival")
    )
    departure_time = (
        test_json.get("data", {}).get("nav", {}).get("route", {}).get("departureTime")
    )
    arrival_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))
    departure_dt = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))
    travel_duration = (arrival_dt - departure_dt).total_seconds()
    print(f"Sleeping for 10 seconds to simulate travel...")
    await asyncio.sleep(10)
    print("JOB DONE, KAFKA WORKS ")
