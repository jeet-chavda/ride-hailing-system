from fastapi import APIRouter
from app.modules.trip import service

router = APIRouter(prefix="/trips", tags=["trip"])


@router.get("/{trip_id}")
def get_trip(trip_id: int):
    return service.get_trip(trip_id)


@router.post("/{trip_id}/transition/{new_status}")
def transition(trip_id: int, new_status: str):
    """Manual override, mainly for testing state transitions from the docs UI."""
    return service.transition(trip_id, new_status.upper())
