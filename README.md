# System Design Foundations & The Big Picture

> **Engineering Behind Ride-Hailing & Mapping Systems** · 9-Week Roadmap

---

## 🚀 MVP Status (added by Claude, Week 1 build)

This repo now contains a **working modular-monolith MVP** implementing the
core flow described below: rider requests a ride → dispatch finds &
locks the nearest online driver → pricing quotes a fare (with surge) →
trip lifecycle is tracked through a state machine → driver location
streams to the rider in real time over WebSocket.

**Run it:**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open `http://127.0.0.1:8000/docs` for interactive API docs (this IS
your API Gateway's contract).

**See it work end-to-end:** `HOWTO_DEMO.md` has copy-pasteable curl
commands that create a rider, two drivers, request a ride, and complete
the trip — the same flow the automated tests in `tests/test_dispatch.py`
exercise.

**Run the tests:**
```bash
pip install pytest httpx
pytest -v
```

**What's real vs. stubbed right now** (this is intentional — see
`app/core/store.py` and `docker-compose.yml`):
| Piece | Current state | Becomes |
|---|---|---|
| Data storage | In-memory Python dicts | PostgreSQL |
| Driver locations / locks / demand counters | In-memory dicts | Redis (GEOADD, Redlock, INCR) |
| Routing | Haversine straight-line distance | A* over a real road graph (Week 2: Dijkstra) |
| Driver location push | In-process WebSocket manager | Redis Pub/Sub fan-out across multiple app servers |

The module boundaries and function signatures are already shaped like the
real thing (see the docstring at the top of each `service.py`), so
swapping the internals later shouldn't require touching the callers.

---

## 🎯 Goals

By the end of this week you should be able to:

- Explain the core services inside an Uber-like system and why each exists
- Distinguish between monolithic and microservice architectures and articulate the trade-offs
- Define latency, throughput, and availability — and explain what "real-time" actually means
- Apply the CAP theorem to a distributed system and reason about trade-offs
- Produce a clear, labelled architecture diagram with correct data-flow arrows

---

## 📚 Topics

| # | Topic |
|---|-------|
| 1 | Monolith vs microservices — trade-offs, when each makes sense |
| 2 | Core services in Uber-like apps: Rider, Driver, Dispatch/Matching, Pricing, Trip, Payments, Maps |
| 3 | Latency, throughput, availability — what "real-time" really means in practice |
| 4 | Sketching architecture diagrams: boxes, arrows, data flow |
| 5 | CAP theorem basics: consistency, availability, partition tolerance |

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Uber Engineering Blog — architecture deep-dives | https://www.uber.com/en-IN/blog/engineering/ |
| System Design Primer — Donne Martin (GitHub) | https://github.com/donnemartin/system-design-primer |
| System Design: Uber (FAANG Senior Engineer) | https://www.youtube.com/watch?v=ZRAE0fUvN_M |
| CAP Theorem Explained — Martin Kleppmann | https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html |

### Recommended Book
> **System Design Interview Vol. 1** — Alex Xu.  
> Chapters 1–3 (scale, estimation, and the interview framework) are directly relevant this week. The book covers rate limiters, consistent hashing, key-value stores, and other distributed systems patterns you'll encounter throughout this roadmap.

---

## ⭐ Deliverable

> **Do not skip this. It is proof you learned the week.**

### Architecture Diagram

Create a **one-page architecture diagram** of your planned mini ride-hailing system using [Excalidraw](https://excalidraw.com) or [draw.io](https://draw.io).

**Requirements — your diagram MUST include all of the following:**

| Component | Notes |
|-----------|-------|
| 🧑 Rider App | Mobile/web client |
| 🚗 Driver App | Mobile client |
| 🔀 API Gateway | Single entry point, handles auth |
| 📡 Dispatch Service | Matching riders ↔ drivers |
| 💰 Pricing Service | Base fare + surge calculation |
| 🗺️ Trip Service | Lifecycle management |
| 🗺️ Map / Routing Service | A* routing, geospatial queries |
| 🐘 PostgreSQL | Primary relational datastore |
| ⚡ Redis | Caching, Pub/Sub, geospatial index |

**Each service must have:**
- A clear label
- Arrows showing which direction data flows
- A brief (2–5 word) annotation on each arrow (e.g. "JWT auth request", "driver lat/lng update")



## 🗂️ Folder Structure

```
week1-system-design/
├── README.md               ← You are here
├── diagrams/
│   ├── architecture.png    ← Your deliverable goes here
│   └── REFLECTION.md       ← Your reflection goes here
├── resources/
│   ├── cap-theorem.md      ← Cheat-sheet notes (provided)
│   ├── monolith-vs-microservices.md
│   └── service-glossary.md
└── starter/
    └── excalidraw-template.excalidraw  ← Optional starter template
```

---



---


