"""
Unit tests for the dispatch/pricing/trip logic, independent of the HTTP
layer. Run with:  pytest

These reset app.core.store between tests since it's a module-level
in-memory store (a smell that goes away once we're on a real DB with
transactional test fixtures — noted as a Week 3+ improvement).
"""
import pytest

from app.core import store
from app.modules.dispatch import service as dispatch
from app.modules.trip import service as trip_service
from app.modules.pricing.service import quote_fare, surge_multiplier
from app.modules.maps.service import haversine_km


@pytest.fixture(autouse=True)
def reset_store():
    store.riders.clear()
    store.drivers.clear()
    store.trips.clear()
    store.driver_locations.clear()
    store.driver_online.clear()
    store.driver_locks.clear()
    store.demand_counters.clear()
    yield


def _add_driver(driver_id, lat, lng, online=True):
    store.drivers[driver_id] = {"id": driver_id, "name": f"Driver {driver_id}"}
    store.driver_online[driver_id] = online
    store.driver_locations[driver_id] = (lat, lng)


def test_matches_nearest_driver():
    _add_driver(1, 19.076, 72.877)   # close
    _add_driver(2, 19.300, 73.100)   # far
    store.riders[1] = {"id": 1, "name": "Rider"}

    result = dispatch.request_ride(1, 19.0760, 72.8777, 19.0330, 72.8570)
    assert result["matched_driver_id"] == 1


def test_locked_driver_is_skipped():
    _add_driver(1, 19.076, 72.877)
    _add_driver(2, 19.077, 72.878)
    store.riders[1] = {"id": 1, "name": "R1"}
    store.riders[2] = {"id": 2, "name": "R2"}

    r1 = dispatch.request_ride(1, 19.076, 72.877, 19.10, 72.90)
    r2 = dispatch.request_ride(2, 19.076, 72.877, 19.10, 72.90)
    assert r1["matched_driver_id"] != r2["matched_driver_id"]


def test_no_drivers_available_raises():
    store.riders[1] = {"id": 1, "name": "R1"}
    with pytest.raises(Exception):
        dispatch.request_ride(1, 19.0, 72.0, 19.1, 72.1)


def test_trip_lifecycle_and_lock_release():
    _add_driver(1, 19.076, 72.877)
    store.riders[1] = {"id": 1, "name": "R1"}
    result = dispatch.request_ride(1, 19.076, 72.877, 19.10, 72.90)
    trip_id = result["trip"]["id"]

    assert store.driver_locks[1] == trip_id

    completed = dispatch.complete_trip(trip_id)
    assert completed["status"] == "COMPLETED"
    assert 1 not in store.driver_locks


def test_invalid_transition_rejected():
    _add_driver(1, 19.076, 72.877)
    store.riders[1] = {"id": 1, "name": "R1"}
    result = dispatch.request_ride(1, 19.076, 72.877, 19.10, 72.90)
    trip_id = result["trip"]["id"]
    dispatch.complete_trip(trip_id)

    with pytest.raises(Exception):
        trip_service.transition(trip_id, "MATCHING")


def test_haversine_known_distance():
    # Roughly Mumbai CST to Mumbai airport, ~15km as the crow flies
    dist = haversine_km(18.9398, 72.8355, 19.0896, 72.8656)
    assert 14 < dist < 18


def test_surge_increases_with_demand():
    for _ in range(5):
        surge_multiplier(19.0, 72.0, online_drivers_nearby=1)
    from app.modules.pricing.service import record_demand
    for _ in range(5):
        record_demand(19.0, 72.0)
    surge = surge_multiplier(19.0, 72.0, online_drivers_nearby=1)
    assert surge > 1.0


def test_fare_quote_shape():
    quote = quote_fare(distance_km=5, duration_min=10, surge=1.5)
    assert quote["total_fare"] > quote["base_fee"]
    assert quote["surge_multiplier"] == 1.5
