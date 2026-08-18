"""
Dispatch / Matching Service
---------------------------
The heart of the product. Orchestrates: find nearby online drivers,
pick the closest one, lock it, ask Pricing for a quote, hand off to
Trip Service to persist state.

Real version: Redis GEORADIUS for the nearest-driver query, Redlock for
the driver lock, WebSocket push to notify the driver, race conditions
between two riders requesting the same driver handled explicitly.

MVP version: linear scan + haversine (fine for a handful of drivers;
this is exactly the piece you'd swap for GEORADIUS once you add Redis --
the function signature below (`find_nearest_online_driver`) is the seam).
"""
from fastapi import HTTPException
from app.core import store
from app.modules.maps.service import haversine_km
from app.modules.pricing import service as pricing
from app.modules.trip import service as trip_service


def find_nearest_online_driver(lat: float, lng: float, exclude: set[int] = frozenset()) -> int | None:
    best_driver = None
    best_dist = float("inf")
    for driver_id, is_online in store.driver_online.items():
        if not is_online or driver_id in exclude:
            continue
        if driver_id not in store.driver_locations:
            continue
        d_lat, d_lng = store.driver_locations[driver_id]
        dist = haversine_km(lat, lng, d_lat, d_lng)
        if dist < best_dist:
            best_dist = dist
            best_driver = driver_id
    return best_driver


def request_ride(rider_id: int, pickup_lat: float, pickup_lng: float,
                  dropoff_lat: float, dropoff_lng: float) -> dict:
    trip = trip_service.create_trip(
        rider_id, (pickup_lat, pickup_lng), (dropoff_lat, dropoff_lng)
    )
    trip_service.transition(trip["id"], "MATCHING")

    pricing.record_demand(pickup_lat, pickup_lng)

    tried = set()
    driver_id = find_nearest_online_driver(pickup_lat, pickup_lng, exclude=tried)
    locked = False
    while driver_id is not None and not locked:
        locked = store.acquire_driver_lock(driver_id, trip["id"])
        if not locked:
            tried.add(driver_id)
            driver_id = find_nearest_online_driver(pickup_lat, pickup_lng, exclude=tried)

    if driver_id is None:
        trip_service.transition(trip["id"], "NO_DRIVERS_FOUND")
        raise HTTPException(status_code=404, detail="no drivers available nearby")

    online_nearby = sum(1 for v in store.driver_online.values() if v)
    surge = pricing.surge_multiplier(pickup_lat, pickup_lng, online_nearby)
    route_info = _route_or_import(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    quote = pricing.quote_fare(route_info["distance_km"], route_info["eta_min"], surge)

    trip["driver_id"] = driver_id
    trip["fare"] = quote
    trip_service.transition(trip["id"], "ACCEPTED")

    return {
        "trip": trip,
        "matched_driver_id": driver_id,
        "route": route_info,
        "fare_quote": quote,
    }


def _route_or_import(lat1, lng1, lat2, lng2):
    # local import avoids a circular import at module load time
    from app.modules.maps.service import route
    return route(lat1, lng1, lat2, lng2)


def complete_trip(trip_id: int) -> dict:
    """
    Walks the trip through its remaining lifecycle: ACCEPTED -> EN_ROUTE ->
    IN_TRIP -> COMPLETED. In the real app, EN_ROUTE and IN_TRIP would be
    separate driver-triggered events (pickup confirmed, dropoff confirmed);
    this endpoint collapses them for the MVP demo so you can see the full
    state machine run without needing a driver client.
    """
    trip = trip_service.get_trip(trip_id)
    if trip["status"] == "ACCEPTED":
        trip_service.transition(trip_id, "EN_ROUTE")
    if trip["status"] == "EN_ROUTE":
        trip_service.transition(trip_id, "IN_TRIP")
    trip_service.transition(trip_id, "COMPLETED")
    if trip["driver_id"] is not None:
        store.release_driver_lock(trip["driver_id"])
    return trip
