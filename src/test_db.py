from src.objects.sol_system import SolSystem
from src.objects.sol_system import SolWaypoints

# Define the reference system symbol
reference_symbol = "X1-MB46"  # Change this to the desired system

sol = SolSystem(reference_symbol)

# 1. Get 10 closest systems
neighbors = sol.get_n_neighbors(n=10)
print("\nClosest systems:")
for neighbor in neighbors:
    print(neighbor)

# 2. Calculate distance to another system
target_symbol = "X1-NX29"  # Replace with an actual system symbol
try:
    distance = sol.distance_to(target_symbol)
    print(f"\nDistance from {reference_symbol} to {target_symbol}: {distance:.2f}")
except ValueError as e:
    print(str(e))

# 3. Get neighbors within a radius
radius = 20.0  # Replace with the desired radius
nearby_systems = sol.get_neighbors_within_radius(radius)
print(f"\nSystems within {radius} units of {reference_symbol}:")
for system in nearby_systems:
    print(system)

# 4. Get all waypoints in the system
waypoints = sol.get_waypoints()
print(f"\nWaypoints in system {reference_symbol}:")
for wp in waypoints:
    print(f"{wp['waypoint_symbol']} - Type: {wp['waypoint_type']}")


waypoint = SolWaypoints("X1-GB49-DE3C")
result = waypoint.get_orbitals()
if result["status"] == "success":
    print(f"Orbitals of {result['planet']}:")
    for orbital in result["orbitals"]:
        print(f" - {orbital['waypoint_symbol']} ({orbital['waypoint_type']})")
else:
    print(result["message"])
