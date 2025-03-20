from src.db.db import init_db, SessionLocal
from src.db.models import Agent, Ship

# Initialize the database (Create tables if not exist)

init_db()
session = SessionLocal()


# # Create an agent (player)
# agent1 = Agent(
#     agent_token="AGENT_12345",
#     current_system="Sol",
#     current_waypoint="Earth",
#     credit=50000,
#     starting_faction="Galactic Union",
# )

# session.add(agent1)
# session.commit()

# # Create ships for the agent
# ship1 = Ship(
#     symbol="USS_ENTERPRISE",
#     agent_id=agent1.id,
#     status="DOCKED",
#     system="Sol",
#     waypoint="Earth",
#     x=100,
#     y=200,
#     crew_current=10,
#     crew_capacity=15,
#     crew_morale=80,
#     fuel_current=500,
#     fuel_capacity=1000,
#     cooldown_seconds=0,
#     engine_type="Warp Drive",
#     engine_speed=9.5,
#     cargo_capacity=500,
#     cargo_units=200,
#     cargo_inventory={"ores": 50, "water": 30},
# )

# ship2 = Ship(
#     symbol="MILLENNIUM_FALCON",
#     agent_id=agent1.id,
#     status="IN_TRANSIT",
#     system="Alpha Centauri",
#     waypoint="Centauri B",
#     x=150,
#     y=300,
#     crew_current=5,
#     crew_capacity=8,
#     crew_morale=90,
#     fuel_current=300,
#     fuel_capacity=600,
#     cooldown_seconds=10,
#     engine_type="Hyperdrive",
#     engine_speed=7.2,
#     cargo_capacity=800,
#     cargo_units=500,
#     cargo_inventory={"spice": 100, "electronics": 200},
# )

# session.add_all([ship1, ship2])
# session.commit()

# Query and print results
# agents = session.query(Agent).all()
# ships = session.query(Ship).all()

# print("Agents in Database:")
# for agent in agents:
#     print(agent)

# print("\nShips in Database:")
# for ship in ships:
#     print(ship)
# Fetch the agent with id=1
agent = session.query(Agent).filter_by(id=1).first()

# Get all ships associated with this agent
if agent:
    ships = agent.ships  # Access relationship
    print(ships)  # List of Ship objects
else:
    print("Agent not found")

session.close()
