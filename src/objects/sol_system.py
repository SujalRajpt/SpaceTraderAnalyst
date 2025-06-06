from typing import List, Dict, Union
from src.db.db_session import get_session
from src.db.models import System, Waypoint
from geoalchemy2.functions import ST_DWithin, ST_Distance


class SolSystem:
    def __init__(self, sol_symbol: str):
        self.sol_symbol = sol_symbol

    def get_n_neighbors(self, n: int = 10) -> List[Dict[str, Union[str, float]]]:
        with get_session() as session:
            reference_system = (
                session.query(System).filter(System.symbol == self.sol_symbol).first()
            )

            if not reference_system:
                print(f"System '{self.sol_symbol}' not found.")
                return []

            closest_systems = (
                session.query(
                    System,
                    ST_Distance(System.location, reference_system.location).label(
                        "distance"
                    ),
                )
                .filter(System.id != reference_system.id)
                .order_by("distance")
                .limit(n)
                .all()
            )

            return [
                {"symbol": s.symbol, "distance": float(d)} for s, d in closest_systems
            ]

    def distance_to(self, other_symbol: str) -> float:
        with get_session() as session:
            reference_system = (
                session.query(System).filter(System.symbol == self.sol_symbol).first()
            )
            other_system = (
                session.query(System).filter(System.symbol == other_symbol).first()
            )

            if not reference_system or not other_system:
                raise ValueError("One or both systems not found.")

            return session.query(
                ST_Distance(reference_system.location, other_system.location)
            ).scalar()

    def get_neighbors_within_radius(
        self, radius: float
    ) -> List[Dict[str, Union[str, float]]]:
        with get_session() as session:
            reference_system = (
                session.query(System).filter(System.symbol == self.sol_symbol).first()
            )

            if not reference_system:
                print(f"System '{self.sol_symbol}' not found.")
                return []

            neighbors = (
                session.query(
                    System,
                    ST_Distance(System.location, reference_system.location).label(
                        "distance"
                    ),
                )
                .filter(ST_DWithin(System.location, reference_system.location, radius))
                .order_by("distance")
                .all()
            )

            return [
                {"symbol": system.symbol, "distance": float(distance)}
                for system, distance in neighbors
            ]

    def get_waypoints(self):
        with get_session() as session:
            # Get the system by symbol
            system = (
                session.query(System).filter(System.symbol == self.sol_symbol).first()
            )

            if not system:
                print(f"System '{self.sol_symbol}' not found!")
                return []

            # Query and extract the waypoints' data eagerly
            waypoints = (
                session.query(Waypoint).filter(Waypoint.system_id == system.id).all()
            )

            # Extract data safely using correct attribute names
            return [
                {
                    "waypoint_symbol": wp.waypoint_symbol,
                    "waypoint_type": wp.waypoint_type,
                }
                for wp in waypoints
            ]


class SolWaypoints:
    def __init__(self, waypoint_symbol: str):
        self.waypoint_symbol = waypoint_symbol
        self.system_symbol = "-".join(self.waypoint_symbol.split("-")[:2])

    def get_orbitals(self):
        with get_session() as session:
            planet = (
                session.query(Waypoint)
                .filter(Waypoint.waypoint_symbol == self.waypoint_symbol)
                .first()
            )

            if not planet:
                return {
                    "status": "error",
                    "message": f"Planet {self.waypoint_symbol} not found in {self.system_symbol}!",
                    "orbitals": [],
                }

            orbitals = (
                session.query(Waypoint)
                .filter(Waypoint.parent_waypoint_id == planet.id)
                .all()
            )

            if orbitals:
                orbital_data = [
                    {
                        "waypoint_symbol": o.waypoint_symbol,
                        "waypoint_type": o.waypoint_type,
                    }
                    for o in orbitals
                ]
                return {
                    "status": "success",
                    "planet": self.waypoint_symbol,
                    "orbitals": orbital_data,
                }
            else:
                return {
                    "status": "success",
                    "planet": self.waypoint_symbol,
                    "message": f"No orbitals found for {self.waypoint_symbol}.",
                    "orbitals": [],
                }

    def fetch_waypoint_details(self):
        with get_session() as session:
            waypoint = (
                session.query(Waypoint)
                .filter_by(waypoint_symbol=self.waypoint_symbol)
                .first()
            )
            parent_waypoint = "None"
            parent_id = waypoint.parent_waypoint_id
            if parent_id:
                parent = session.query(System).filter(System.id == parent_id).first()
                parent_waypoint = parent.symbol
            return {
                "waypoint_id": waypoint.id,
                "Waypoint_Symbol": waypoint.waypoint_symbol,
                "waypoint_type": waypoint.waypoint_type,
                "parent_waypoint": parent_waypoint,
            }
