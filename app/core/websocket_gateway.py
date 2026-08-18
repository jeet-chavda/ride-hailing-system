"""
WebSocket Gateway
-----------------
Real version: Redis Pub/Sub fans this out across multiple app server
instances. MVP version: a single-process ConnectionManager, since we only
have one server instance right now. The Pub/Sub-shaped interface
(`broadcast_to_trip`) is kept the same so swapping in real Redis Pub/Sub
later is a one-file change, not a rewrite of every caller.
"""
from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        # trip_id -> set of websocket connections watching that trip
        self.subscribers: dict[int, set[WebSocket]] = defaultdict(set)

    async def subscribe(self, trip_id: int, websocket: WebSocket):
        await websocket.accept()
        self.subscribers[trip_id].add(websocket)

    def unsubscribe(self, trip_id: int, websocket: WebSocket):
        self.subscribers[trip_id].discard(websocket)

    async def broadcast_to_trip(self, trip_id: int, message: dict):
        dead = []
        for ws in self.subscribers.get(trip_id, set()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unsubscribe(trip_id, ws)


manager = ConnectionManager()
