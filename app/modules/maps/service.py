"""
Map / Routing Service
----------------------
Real version (per README): A* over an OSM road graph via OSMnx, or a hosted
API like Mapbox Directions.

MVP version: straight-line (haversine) distance + a fixed average speed
assumption for ETA. This is intentionally the simplest possible stand-in --
the point of Week 1-2 is the *service boundary*, not the routing algorithm.
Week 2 of the roadmap (Dijkstra) is where real graph routing gets built;
swap this function's internals then and nothing calling it has to change.
"""
import math

AVG_SPEED_KMPH = 30.0  # naive city-traffic assumption


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points, in kilometers."""
    r = 6371.0  # Earth radius, km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def route(lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    distance_km = haversine_km(lat1, lng1, lat2, lng2)
    eta_min = (distance_km / AVG_SPEED_KMPH) * 60
    return {
        "distance_km": round(distance_km, 3),
        "eta_min": round(eta_min, 1),
    }
