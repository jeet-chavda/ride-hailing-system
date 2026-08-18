from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.maps import service

router = APIRouter(prefix="/maps", tags=["maps"])


class RouteRequest(BaseModel):
    lat1: float
    lng1: float
    lat2: float
    lng2: float


@router.post("/route")
def get_route(payload: RouteRequest):
    return service.route(payload.lat1, payload.lng1, payload.lat2, payload.lng2)
