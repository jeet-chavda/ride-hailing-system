# Service Glossary — Ride-Hailing Architecture

A quick reference for every service that appears in your Week 1 architecture diagram.

---

## Core Services

### 🧑 Rider App
**What it is:** The mobile/web interface used by passengers.  
**Responsibilities:** Login/signup, request a ride, view fare quote, track driver on map, rate the trip.  
**Talks to:** API Gateway only. Never directly to backend services.

---

### 🚗 Driver App
**What it is:** The mobile interface used by drivers.  
**Responsibilities:** Toggle online/offline, stream location updates, accept/decline ride requests, confirm pickup & dropoff.  
**Talks to:** API Gateway + WebSocket server for real-time updates.

---

### 🔀 API Gateway
**What it is:** The single entry point for all client traffic.  
**Responsibilities:** Authentication (JWT validation), rate limiting, request routing to the correct backend service, SSL termination.  
**Why it exists:** Clients shouldn't know the internal structure of your services. The gateway is the public contract.  
**Tech options:** Kong, AWS API Gateway, Nginx, or a custom Express/FastAPI app.

---

### 📡 Dispatch / Matching Service
**What it is:** The heart of the product — matches riders to drivers.  
**Responsibilities:** Receive ride requests, query nearby drivers (via geospatial index), acquire distributed lock on a driver, notify driver via WebSocket, handle accept/decline + timeouts, manage trip state machine.  
**Why it's complex:** Race conditions (two riders requesting the same driver), timeouts, re-matching logic.  
**Data store:** Redis (driver state, locks) + PostgreSQL (trip records).

---

### 💰 Pricing Service
**What it is:** Calculates fares in real time.  
**Responsibilities:** Compute base fare, per-km fare, per-minute fare, apply surge multiplier based on local demand/supply ratio.  
**Formula:** `Fare = base_fee + (per_km × distance_km) + (per_min × duration_min) × surge_multiplier`  
**Data store:** Redis (demand/supply counts per H3 cell).

---

### 🗓️ Trip Service
**What it is:** Manages the full lifecycle of a trip.  
**Responsibilities:** Create trip record on request, update status at each state transition (requested → matching → accepted → en-route → in-trip → completed → rated), store final fare.  
**Data store:** PostgreSQL.

---

### 🗺️ Map / Routing Service
**What it is:** Answers spatial questions.  
**Responsibilities:** Given two lat/lng points, return the shortest route (A* on road graph), return ETA, return distance.  
**Data store:** Road graph in memory or PostGIS. OSM data as source.  
**Tech options:** OSMnx (Python) to load OpenStreetMap data, or a hosted API like Mapbox Directions API.

---

### 🐘 PostgreSQL
**What it is:** The primary relational database.  
**Stores:** users, drivers, trips, payments, ratings.  
**Why PostgreSQL specifically?** PostGIS extension adds native geospatial types and indexes (`ST_Distance`, `ST_Within`) — essential for a mapping system.

---

### ⚡ Redis
**What it is:** An in-memory data structure store used for multiple purposes.

| Use case | How |
|----------|-----|
| Driver locations (geospatial index) | `GEOADD`, `GEORADIUS` commands |
| Online/offline driver state | Key-value with TTL |
| Distributed locks (Redlock) | Prevents double-booking |
| Pub/Sub for WebSocket fan-out | `PUBLISH` / `SUBSCRIBE` channels |
| Surge pricing demand counters | Atomic `INCR` per H3 cell |

---

## Data Flow Summary

```
Rider requests ride
      │
      ▼
API Gateway (validates JWT)
      │
      ▼
Dispatch Service
      ├── Pricing Service → returns fare quote
      ├── Redis GEORADIUS → finds 5 nearest drivers
      ├── Redis Redlock → locks chosen driver
      ├── WebSocket Server → notifies driver
      └── PostgreSQL → creates trip record
            │
            ▼ (driver accepts)
      Trip Service updates state → EN_ROUTE
            │
            ▼ (real-time)
      WebSocket broadcasts driver location to rider
            │
            ▼ (trip ends)
      Pricing Service → calculates final fare
      PostgreSQL → stores completed trip
```

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Latency** | Time from request sent to response received. Target: < 200ms for API calls, < 100ms for WebSocket updates |
| **Throughput** | Requests per second the system can handle. Uber peak: millions of requests/sec |
| **Availability** | % of time the system is up. "Five nines" = 99.999% = ~5 min downtime/year |
| **Idempotency** | Sending the same request twice has the same effect as sending it once. Critical for payments and trip creation |
| **Eventual consistency** | All nodes will *eventually* agree on the same value, but not necessarily right now |
| **TTL** | Time To Live — how long a cached value is valid before expiry |
