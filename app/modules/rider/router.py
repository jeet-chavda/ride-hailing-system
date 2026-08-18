from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import store

router = APIRouter(prefix="/riders", tags=["rider"])


class RiderCreate(BaseModel):
    name: str


@router.post("")
def create_rider(payload: RiderCreate):
    rider_id = store.next_id()
    store.riders[rider_id] = {"id": rider_id, "name": payload.name}
    return store.riders[rider_id]


@router.get("/{rider_id}")
def get_rider(rider_id: int):
    if rider_id not in store.riders:
        raise HTTPException(status_code=404, detail="rider not found")
    return store.riders[rider_id]
