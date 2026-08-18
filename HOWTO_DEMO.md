# Demo Walkthrough (curl)

Start the server first: `uvicorn app.main:app --reload`

All commands assume the server is on `http://127.0.0.1:8000`.

## 1. Create a rider
```bash
curl -s -X POST http://127.0.0.1:8000/riders \
  -H "Content-Type: application/json" \
  -d '{"name": "Asha"}'
```
→ note the returned `id`, you'll use it as `rider_id` below.

## 2. Create two drivers
```bash
curl -s -X POST http://127.0.0.1:8000/drivers -H "Content-Type: application/json" -d '{"name": "Ravi"}'
curl -s -X POST http://127.0.0.1:8000/drivers -H "Content-Type: application/json" -d '{"name": "Kabir"}'
```

## 3. Bring both online and set their locations
(swap `1` / `2` for whatever ids you actually got back)
```bash
curl -s -X POST http://127.0.0.1:8000/drivers/1/online
curl -s -X POST http://127.0.0.1:8000/drivers/1/location \
  -H "Content-Type: application/json" -d '{"lat": 19.0760, "lng": 72.8777}'

curl -s -X POST http://127.0.0.1:8000/drivers/2/online
curl -s -X POST http://127.0.0.1:8000/drivers/2/location \
  -H "Content-Type: application/json" -d '{"lat": 19.2000, "lng": 73.0000}'
```

## 4. Request a ride (rider_id from step 1)
```bash
curl -s -X POST http://127.0.0.1:8000/dispatch/request \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": 1,
    "pickup_lat": 19.0761, "pickup_lng": 72.8778,
    "dropoff_lat": 19.0330, "dropoff_lng": 72.8570
  }'
```
You should see `matched_driver_id: 1` (the closer driver), a `route`
(distance + ETA), and a `fare_quote`. Note the returned `trip.id`.

## 5. Check trip status
```bash
curl -s http://127.0.0.1:8000/trips/<trip_id>
```

## 6. Complete the trip
```bash
curl -s -X POST http://127.0.0.1:8000/dispatch/<trip_id>/complete
```
Status should now be `COMPLETED`, and driver 1's lock is released — request
another ride and driver 1 becomes eligible again.

## 7. Watch live driver location (optional, needs a WebSocket client)
With a tool like `websocat` or `wscat`:
```bash
wscat -c ws://127.0.0.1:8000/ws/trips/<trip_id>
```
Then in another terminal, push a location update for the matched driver —
you should see it arrive instantly on the WebSocket connection:
```bash
curl -s -X POST http://127.0.0.1:8000/drivers/1/location \
  -H "Content-Type: application/json" -d '{"lat": 19.070, "lng": 72.870}'
```

## 8. Try the failure case: no drivers available
Set both drivers offline, then request a ride again — you should get a
404 with `"no drivers available nearby"`. This is the `NO_DRIVERS_FOUND`
branch of the trip state machine.
```bash
curl -s -X POST http://127.0.0.1:8000/drivers/1/offline
curl -s -X POST http://127.0.0.1:8000/drivers/2/offline
curl -s -X POST http://127.0.0.1:8000/dispatch/request \
  -H "Content-Type: application/json" \
  -d '{"rider_id": 1, "pickup_lat": 19.0, "pickup_lng": 72.0, "dropoff_lat": 19.1, "dropoff_lng": 72.1}'
```
