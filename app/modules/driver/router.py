from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import store
from app.core.websocket_gateway import manager

router = APIRouter(prefix="/drivers", tags=["driver"])


class DriverCreate(BaseModel):
    name: str


class LocationUpdate(BaseModel):
    lat: float
    lng: float


@router.post("")
def create_driver(payload: DriverCreate):
    driver_id = store.next_id()
    store.drivers[driver_id] = {"id": driver_id, "name": payload.name}
    store.driver_online[driver_id] = False
    return store.drivers[driver_id]


@router.post("/{driver_id}/online")
def go_online(driver_id: int):
    _require_driver(driver_id)
    store.driver_online[driver_id] = True
    return {"driver_id": driver_id, "online": True}


@router.post("/{driver_id}/offline")
def go_offline(driver_id: int):
    _require_driver(driver_id)
    store.driver_online[driver_id] = False
    store.driver_locations.pop(driver_id, None)
    return {"driver_id": driver_id, "online": False}


@router.post("/{driver_id}/location")
async def update_location(driver_id: int, payload: LocationUpdate):
    """
    Real version: this hits Redis GEOADD and fans out via Pub/Sub to any
    rider currently watching this driver's trip (see websocket_gateway.py).
    MVP: update the in-memory dict, and if this driver currently holds a
    trip lock, push the new location straight to that trip's WebSocket
    subscribers.
    """
    _require_driver(driver_id)
    store.driver_locations[driver_id] = (payload.lat, payload.lng)

    active_trip_id = store.driver_locks.get(driver_id)
    if active_trip_id is not None:
        await manager.broadcast_to_trip(
            active_trip_id,
            {"driver_id": driver_id, "lat": payload.lat, "lng": payload.lng},
        )

    return {"driver_id": driver_id, "lat": payload.lat, "lng": payload.lng}


def _require_driver(driver_id: int):
    if driver_id not in store.drivers:
        raise HTTPException(status_code=404, detail="driver not found")
