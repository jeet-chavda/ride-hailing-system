from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.dispatch import service

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


class RideRequest(BaseModel):
    rider_id: int
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float


@router.post("/request")
def request_ride(payload: RideRequest):
    return service.request_ride(
        payload.rider_id,
        payload.pickup_lat,
        payload.pickup_lng,
        payload.dropoff_lat,
        payload.dropoff_lng,
    )


@router.post("/{trip_id}/complete")
def complete_trip(trip_id: int):
    return service.complete_trip(trip_id)
