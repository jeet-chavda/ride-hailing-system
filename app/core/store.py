"""
In-memory data store for the MVP.

Why in-memory and not Postgres/Redis yet?
------------------------------------------
The Week 1 roadmap targets a *modular monolith that looks like microservices*:
same service boundaries and interfaces you'd have with real services, but
without the operational overhead while you're still learning the domain.

This module plays the role that PostgreSQL + Redis will play later:
  - `trips`, `users`, `drivers`  -> will move to PostgreSQL
  - `driver_locations`, `driver_online`, `locks` -> will move to Redis

When you're ready (roadmap mentions this as a stretch goal), swap the
functions in this file for real DB/Redis calls. Every module below only
talks to *this* file, never to a raw dict directly -- that's the seam
you'll cut along when you extract real services.
"""
from __future__ import annotations
import itertools
import threading
from typing import Optional

_lock = threading.Lock()
_id_counter = itertools.count(1)


def next_id() -> int:
    return next(_id_counter)


# --- "PostgreSQL" tables (plain dicts keyed by id) -------------------------
riders: dict[int, dict] = {}
drivers: dict[int, dict] = {}
trips: dict[int, dict] = {}

# --- "Redis" state -----------------------------------------------------
driver_locations: dict[int, tuple[float, float]] = {}   # driver_id -> (lat, lng)
driver_online: dict[int, bool] = {}                       # driver_id -> bool
driver_locks: dict[int, int] = {}                         # driver_id -> trip_id holding the lock
demand_counters: dict[str, int] = {}                       # h3-ish cell key -> request count


def acquire_driver_lock(driver_id: int, trip_id: int) -> bool:
    """Simulates a Redis Redlock: only one trip can hold a driver at a time."""
    with _lock:
        if driver_id in driver_locks:
            return False
        driver_locks[driver_id] = trip_id
        return True


def release_driver_lock(driver_id: int) -> None:
    with _lock:
        driver_locks.pop(driver_id, None)
