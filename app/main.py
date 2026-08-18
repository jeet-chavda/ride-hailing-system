"""
Ride-Hailing System — Modular Monolith MVP
============================================
Entry point. Wires together the six service modules (rider, driver,
dispatch, pricing, trip, maps) behind a single API Gateway process.

Run:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for interactive API docs (this IS
your API Gateway's contract — the same one a real gateway like Kong or
AWS API Gateway would expose to clients).
"""
from fastapi import FastAPI

from app.modules.rider.router import router as rider_router
from app.modules.driver.router import router as driver_router
from app.modules.dispatch.router import router as dispatch_router
from app.modules.trip.router import router as trip_router
from app.modules.maps.router import router as maps_router
from app.modules.realtime.router import router as realtime_router

app = FastAPI(
    title="Ride-Hailing System (MVP)",
    description=(
        "A modular monolith implementing the core Uber-like flow: "
        "rider requests a ride -> dispatch finds & locks a driver -> "
        "pricing quotes a fare -> trip lifecycle is tracked -> driver "
        "location streams to the rider over WebSocket."
    ),
    version="0.1.0",
)

app.include_router(rider_router)
app.include_router(driver_router)
app.include_router(dispatch_router)
app.include_router(trip_router)
app.include_router(maps_router)
app.include_router(realtime_router)


@app.get("/health")
def health():
    return {"status": "ok"}
