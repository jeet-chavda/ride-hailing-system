# Monolith vs Microservices — Notes

---

## What is a Monolith?

All application logic deployed as **a single unit**. One codebase, one deployment, one database.

```
[ Rider Logic | Driver Logic | Dispatch | Pricing | Trips | Maps ]
                        ↓
                  Single Database
```

### Pros
- Simple to develop and test locally
- No network calls between components (fast in-process calls)
- Easy to deploy — one binary
- Easier to reason about transactions (ACID across all data)

### Cons
- A bug in Pricing can crash the entire app
- Scaling means scaling *everything*, even if only Dispatch is under load
- Long-term: large codebase becomes hard to navigate
- Teams step on each other's work

---

## What are Microservices?

Application split into **small, independently deployable services**, each owning its own data.

```
[ Rider Service ] ←→ [ API Gateway ] ←→ [ Dispatch Service ]
                           ↕                      ↕
                    [ Pricing Service ]    [ Trip Service ]
                           ↕                      ↕
                    [ Maps Service  ]      [ Driver Service ]
                           ↕
                    (Each service has its own DB / cache)
```

### Pros
- Independent deployment — update Pricing without touching Dispatch
- Independent scaling — run 10 Dispatch instances, 1 Pricing instance
- Fault isolation — Pricing crash doesn't kill Dispatch
- Teams own their service end-to-end

### Cons
- Network calls add latency and can fail
- Distributed transactions are hard (no simple ACID across services)
- Operational complexity: monitoring, tracing, service discovery
- Data consistency is harder — eventual consistency must be embraced

---

## The Real Trade-off

| Factor | Monolith | Microservices |
|--------|----------|---------------|
| **Team size** | Works well for small teams (< ~8 engineers) | Designed for large organisations |
| **Operational maturity** | Low — just deploy one thing | High — needs Kubernetes, service mesh, distributed tracing |
| **Development speed (early)** | Fast | Slower (infrastructure overhead) |
| **Development speed (at scale)** | Slows down (coupling) | Stays fast (independence) |
| **Debugging** | Easy — one log stream | Hard — traces cross multiple services |
| **Testing** | Easy — integration tests are local | Hard — need contract testing, mocks |

---

## What Should You Build for This Roadmap?

**Recommended: a modular monolith that *looks like* microservices.**

- Single codebase, but with clearly separated modules/folders per service
- One database, but with clear schema boundaries
- Same REST interfaces you'd expose if they were real services
- This gives you the conceptual understanding without Kubernetes overhead

When you're comfortable, you can extract one module into a real separate service as a stretch goal.

---

## How Uber Actually Did It

Uber started as a **monolith** (Python + SQLAlchemy). By 2014 they were at 40 engineers and the monolith was breaking down. They migrated to microservices over 2015–2016.

By 2020 they had **2,200+ microservices**. That introduced its own coordination problems — which is why they now advocate for "domain-oriented microservice architecture" (grouping related services).

**Lesson:** Start simple. Complexity is earned, not assumed.

---

## Further Reading

- Martin Fowler on Microservices: https://martinfowler.com/articles/microservices.html
- Uber's migration story: https://www.uber.com/en-IN/blog/engineering/
- "Microservices Premium" — when it's *not* worth it: https://martinfowler.com/bliki/MicroservicePremium.html
