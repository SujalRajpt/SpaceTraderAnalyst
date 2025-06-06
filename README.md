# 🚀 SpaceTraders Game Simulator & Analyst

This project is a **real-time space trading simulation engine** built on top of the [SpaceTraders.io](https://spacetraders.io/) API. It simulates player actions such as travel, mining, and market interaction with realistic delays and state tracking. The system also includes a database-backed backend with route planning, fuel tracking, and early support for predictive analytics.

---

## 🛠️ Features

### ✅ Real-Time Game Simulation
- Asynchronous event handling (e.g., travel, mining, docking).
- Uses `asyncio` to simulate real-time travel durations.
- Event consumers powered by **Kafka**.

### 🌌 Universe Mapping & Navigation
- Complete universe mapped and stored with coordinates using **PostGIS**.
- Real-time ship location updates and travel path simulation.
- Distance calculation between waypoints using geospatial data.

### 🚢 Ship Management
- Tracks individual ships’ fuel, location, navigation state (DOCKED, IN_ORBIT, IN_TRANSIT).
- Automatically transitions between DOCKED ↔ ORBIT ↔ TRANSIT.
- Logs all trips with timestamps and travel durations.

### ⛽ Fuel & Travel Analytics
- Logs fuel usage for all travel events.
- Warns when a trip might fail due to insufficient fuel.
- Plans for ML-based prediction of fuel requirements based on:
  - Ship type
  - Distance
  - Historical travel logs

### 🧠 Planned Enhancements
- Smart `start_trip` validator with fuel & cooldown checks.
- Predictive travel planning (ETA, refuel suggestions).
- Streamlit dashboard to visualize universe, ship paths, and analytics.
- Autonomous trader bot to monitor markets and plan profitable trades.

---

## 🧱 Tech Stack

| Layer            | Tools / Libraries                             |
|------------------|----------------------------------------------|
| Backend Engine   | Python, `asyncio`, `requests`, `FastAPI` (optional) |
| Messaging Queue  | Kafka (Confluent-compatible)                  |
| Database         | PostgreSQL with PostGIS extension             |
| ORM              | SQLAlchemy                                    |
| Geospatial Logic | PostGIS, Shapely                              |
| ML Pipeline (WIP)| Scikit-learn, pandas (planned)                |
| Infrastructure   | Docker, Kafka CLI, Python dotenv              |

---


## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Kafka & Zookeeper (local or Confluent Cloud)

### Installation

```bash
git clone https://github.com/your-username/SpaceTraderAnalyst.git
cd SpaceTraderAnalyst
python -m venv env
source env/bin/activate  # or `.\env\Scripts\activate` on Windows
pip install -r requirements.txt
