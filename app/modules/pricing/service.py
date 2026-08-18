"""
Pricing Service
---------------
Fare = base_fee + (per_km * distance_km) + (per_min * duration_min) * surge_multiplier

Surge multiplier is derived from a demand/supply ratio for a coarse
geo-cell (a real system uses H3 cells; here we round lat/lng to 2 decimal
places -- roughly ~1km grid -- as a stand-in worth revisiting once you
add H3 in a later week).
"""
from app.core import store

BASE_FEE = 40.0
PER_KM = 12.0
PER_MIN = 1.5


def cell_key(lat: float, lng: float) -> str:
    return f"{round(lat, 2)}:{round(lng, 2)}"


def record_demand(lat: float, lng: float) -> None:
    key = cell_key(lat, lng)
    store.demand_counters[key] = store.demand_counters.get(key, 0) + 1


def surge_multiplier(lat: float, lng: float, online_drivers_nearby: int) -> float:
    key = cell_key(lat, lng)
    demand = store.demand_counters.get(key, 0)
    supply = max(online_drivers_nearby, 1)
    ratio = demand / supply
    if ratio <= 1:
        return 1.0
    if ratio <= 2:
        return 1.3
    if ratio <= 4:
        return 1.7
    return 2.2


def quote_fare(distance_km: float, duration_min: float, surge: float = 1.0) -> dict:
    fare = BASE_FEE + (PER_KM * distance_km) + (PER_MIN * duration_min * surge)
    return {
        "base_fee": BASE_FEE,
        "distance_component": round(PER_KM * distance_km, 2),
        "time_component": round(PER_MIN * duration_min * surge, 2),
        "surge_multiplier": surge,
        "total_fare": round(fare, 2),
    }
