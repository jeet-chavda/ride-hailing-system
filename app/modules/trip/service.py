r"""
Trip Service
------------
Owns the trip lifecycle state machine:

  REQUESTED -> MATCHING -> ACCEPTED -> EN_ROUTE -> IN_TRIP -> COMPLETED
                  \-> NO_DRIVERS_FOUND            \-> CANCELLED

Real version stores this in PostgreSQL with proper transitions guarded by
DB constraints. MVP keeps it in-memory but the transition rules below are
the same rules you'd enforce with a CHECK constraint or an ORM state
machine library later.
"""
from fastapi import HTTPException
from app.core import store

VALID_TRANSITIONS = {
    "REQUESTED": {"MATCHING", "CANCELLED"},
    "MATCHING": {"ACCEPTED", "NO_DRIVERS_FOUND", "CANCELLED"},
    "ACCEPTED": {"EN_ROUTE", "CANCELLED"},
    "EN_ROUTE": {"IN_TRIP", "CANCELLED"},
    "IN_TRIP": {"COMPLETED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
    "NO_DRIVERS_FOUND": set(),
}


def create_trip(rider_id: int, pickup: tuple, dropoff: tuple) -> dict:
    trip_id = store.next_id()
    trip = {
        "id": trip_id,
        "rider_id": rider_id,
        "driver_id": None,
        "pickup": pickup,
        "dropoff": dropoff,
        "status": "REQUESTED",
        "fare": None,
    }
    store.trips[trip_id] = trip
    return trip


def transition(trip_id: int, new_status: str) -> dict:
    trip = get_trip(trip_id)
    current = trip["status"]
    if new_status not in VALID_TRANSITIONS.get(current, set()):
        raise HTTPException(
            status_code=409,
            detail=f"invalid transition {current} -> {new_status}",
        )
    trip["status"] = new_status
    return trip


def get_trip(trip_id: int) -> dict:
    trip = store.trips.get(trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="trip not found")
    return trip
