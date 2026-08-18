# CAP Theorem — Cheat Sheet

> Formulated by Eric Brewer (2000). Formally proved by Gilbert & Lynch (2002).

---

## The Three Properties

### Consistency (C)
Every read receives the **most recent write** or an error.  
All nodes see the same data at the same time.

> Example: You update your profile picture. Any server you hit immediately returns the new picture.

### Availability (A)
Every request receives a **response** (not necessarily the most recent data) — the system never returns an error.

> Example: Even if some servers are down, you always get *some* response.

### Partition Tolerance (P)
The system continues operating even if **network messages are dropped** or delayed between nodes (a "network partition").

> Example: The EU datacenter loses its connection to the US datacenter for 30 seconds. The system keeps working in both regions.

---

## The Theorem

> **A distributed system can guarantee at most 2 of the 3 properties simultaneously.**

In practice, **network partitions always happen** (cables get cut, routers fail, packets get lost). This means **P is not optional** for any real distributed system.

The real choice is: **CP or AP?**

---

## CP vs AP in Practice

| Choice | Behaviour during a partition | Example systems |
|--------|------------------------------|-----------------|
| **CP** | Returns an error rather than stale data | HBase, Zookeeper, etcd |
| **AP** | Returns potentially stale data rather than an error | Cassandra, DynamoDB, CouchDB |

---

## How This Applies to a Ride-Hailing System

| Component | Choice | Why |
|-----------|--------|-----|
| PostgreSQL (trips, users) | **CP** | Trip state must be consistent — you can't double-book a driver |
| Redis (driver locations) | **AP** | A slightly stale location (1–3 seconds old) is fine; availability matters more |
| Pricing Service | **CP** | The fare shown to a rider must match what's charged |
| Driver online/offline status | **AP** | Brief stale status is tolerable; availability is critical |

---

## Common Misconceptions

❌ "CA systems exist" — They don't at scale. Without partition tolerance you have a single node.  
❌ "You pick two, ignore the third" — You pick your trade-off *during a partition*. Normal operation can satisfy all three.  
❌ "Consistency = ACID" — CAP consistency ≠ database ACID consistency. They're related but different concepts.

---

## Key Quote

> *"The CAP theorem is a starting point for conversation, not an excuse to give up on consistency."*  
> — Martin Kleppmann, *Designing Data-Intensive Applications*

---

## Further Reading

- Martin Kleppmann's critique of CAP: https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html  
- Gilbert & Lynch original paper: https://dl.acm.org/doi/10.1145/564585.564601
