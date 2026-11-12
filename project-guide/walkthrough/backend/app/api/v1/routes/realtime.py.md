# backend/app/api/v1/routes/realtime.py

## 1. Purpose
This file opens **WebSocket** endpoints. A WebSocket is a connection that stays open so the server can push messages at any time (normal HTTP is one question, one answer, then closed). The passenger app listens for ride status. The driver app listens for ride offers. It uses `realtime_hub` (`backend/app/services/realtime_service.py`) to keep the list of open connections.

## 2. Imports, one by one
**Third-party**
- `import jwt` (`realtime.py:1`). This is **PyJWT**. A **JWT** (JSON Web Token) is a signed text that proves who you are. *Example:* `jwt.decode(token, key, algorithms=['HS256'])` returns the data inside, or raises an error if the signature is wrong or expired.
- `from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status` (`:2`). `WebSocket` is the connection object. `WebSocketDisconnect` is raised when the client leaves. `status` holds named codes, such as `status.WS_1008_POLICY_VIOLATION` (= 1008, "you broke a rule").
- `from sqlalchemy.orm import Session` (`:3`). Type hint for the database session.

**Project**
- `get_settings` from `app/core/config.py` (`:5`): gives `jwt_secret_key` and `jwt_algorithm`.
- `SessionLocal` from `app/db.py` (`:6`): a factory that makes a new session by hand (needed because WebSocket routes here do not use `Depends(get_db)`).
- `Driver, Ride` from `app/models/ride_hailing.py` (`:7`); `Passenger` from `app/models/user.py` (`:8`).
- `driver_channel, passenger_channel` from `app/services/realtime_events.py` (`:9`): build channel names (text keys such as one per ride).
- `realtime_hub` from `app/services/realtime_service.py` (`:10`): the shared object that stores sockets per channel and sends to them.
- `RideMatchingService` from `app/services/ride_matching_service.py` (`:11`): gives the current ride status and the current offer.

## 3. Walk through the code, top to bottom
- `router = APIRouter(prefix='/realtime', tags=['realtime'])` (`:13`).
- `_bearer_token(websocket) -> str | None` (`:16-18`). Reads the `authorization` header. If it starts with `bearer ` (case-insensitive), returns the text after the first 7 characters. Else `None`. *Example:* `"Bearer abc"` -> `"abc"`.
- `_decode(websocket, actor) -> int | None` (`:21-35`). Returns the user id or `None`.
  - No token -> `None` (`:23-24`).
  - `jwt.decode(token, secret, algorithms=[...])` (`:26-30`) checks the signature and expiry and returns the payload dict. Pinning `algorithms` is a security must.
  - `payload.get('type') != 'access' or payload.get('actor') != actor` (`:31`): the token must be an access token (not a refresh token) and made for this kind of user. Passengers pass `actor=None` (their tokens have no `actor` claim; I infer this from the code, check `app/core/security.py`). Drivers pass `'driver'`.
  - `int(payload['sub'])` (`:33`): `sub` (subject) holds the user id.
  - Any of `jwt.PyJWTError, KeyError, TypeError, ValueError` -> `None` (`:34-35`).
- `_keep_alive(websocket, channel)` (`:38-47`), `async`. Loops forever: `await websocket.receive_text()` waits for a text message. **await** means "pause here until the result is ready, let other work run". If it equals `'ping'`, `send_json({'type':'pong'})` answers. This keeps the connection alive and detects dead clients. On `WebSocketDisconnect` it ends quietly. `finally` always runs `realtime_hub.disconnect(channel, websocket)` to forget the socket.
- `@router.websocket('/passengers/rides/{ride_id}')` -> `passenger_ride_events` (`:50-66`):
  1. `_decode(websocket, None)` gets the passenger id.
  2. `SessionLocal()` opens a session by hand (`:53`).
  3. Loads `Passenger` and `Ride` with `db.get(Model, id)` (returns the row or `None`) (`:55-56`).
  4. If missing or `ride.passenger_id != passenger.id`, close with code 1008 and return (`:57-59`). This stops people from watching other people's rides.
  5. `channel = passenger_channel(passenger.id, ride.id)`; `await realtime_hub.connect(channel, websocket)` registers the socket (and, I believe, accepts it; check `realtime_service.py`).
  6. Sends first message `ride.status` with a snapshot: `snapshot.model_dump(mode='json')` turns a Pydantic object into plain JSON-safe data (`:62-63`).
  7. `await _keep_alive(...)` runs until disconnect.
  8. `finally: db.close()` returns the session (`:65-66`).
- `@router.websocket('/drivers/me')` -> `driver_events` (`:69-89`): same shape. Decode with `'driver'`; reject if no driver or status is `suspended` or `deactivated` (`:75`). Connects to `driver_channel(driver.id)`. Sends first message `ride.offer` with the current offer, or `ride.offer_cleared` with `data: None` (`:81-86`).

Errors: none raised to the client. Bad auth ends with close code 1008.

## 4. How data flows
```
Driver app --WS /realtime/drivers/me + Authorization: Bearer--> driver_events
  _decode -> driver_id -> db.get(Driver) -> status ok?
  hub.connect(driver:ID) -> send {"type":"ride.offer",...}
  loop: recv "ping" -> send {"type":"pong"}
Elsewhere (matching service) -> hub.send(channel, event) -> Driver app
Disconnect -> hub.disconnect
```

## 5. Try it
Install the tool once, then connect:
```zsh
uvx websocat -H="Authorization: Bearer <token>" ws://127.0.0.1:8000/realtime/drivers/me
```
I am not sure `uvx websocat` works (websocat is a Rust tool); install it with `pacman -S websocat` if needed. Type `ping` and press Enter. Expected: first a `ride.offer_cleared` line, then `{"type":"pong"}`.

## 6. Can it be better?
- Good: ownership check for ride, driver status check, access-type check, clean-up in `finally`.
- Weak: the token is read only from the header (`:17`). Browsers cannot set headers on WebSockets, so a web admin would fail; native apps are fine. A database session is held open for the whole connection (`:53`, closed at `:66`), which can exhaust the connection pool with many users. `get_settings()` is called twice (`:28-29`). `_decode` has no logging. The `ping` text is a magic string. A token that expires mid-connection is not re-checked. If `close` happens before accept, clients usually see an HTTP 403 and not code 1008 (simplified; check Starlette docs).
- Cleaner way: open the session only for the first query, then close it before `_keep_alive`:
  ```python
  with SessionLocal() as db:
      ...build snapshot...
  await _keep_alive(websocket, channel)
  ```
- Security: tokens in headers stay out of logs, which is good. Never put the token in the URL.

## 7. Check yourself
1. Why does `_decode` compare `payload.get('actor')` with the `actor` argument?
2. What does the `finally` in `_keep_alive` guarantee?
