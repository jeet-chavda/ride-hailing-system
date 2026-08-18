from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_gateway import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/trips/{trip_id}")
async def watch_trip(websocket: WebSocket, trip_id: int):
    """
    A rider's app connects here after a trip is ACCEPTED to receive live
    driver-location pushes. Try it with the `wscat` CLI or the small
    test script in tests/test_websocket_demo.py.
    """
    await manager.subscribe(trip_id, websocket)
    try:
        while True:
            # Rider client doesn't need to send anything; this just keeps
            # the connection open and detects disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.unsubscribe(trip_id, websocket)
