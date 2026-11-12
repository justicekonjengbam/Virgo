# backend/tests/unit/test_realtime_service.py

## 1. Purpose
Tests `RealtimeHub` (`backend/app/services/realtime_service.py:8`), the class that pushes live messages (ride status changes) to apps over **WebSockets** (a connection that stays open so the server can send messages any time. *Example:* a chat app). The test uses a fake socket instead of a real one.

## 2. Imports, one by one
- `import pytest` (`:1`). Test runner. Used for `@pytest.mark.asyncio`.
- `from app.services.realtime_service import RealtimeHub` (`:3`). The class under test.

## 3. Walk through the code
### `class FakeWebSocket` (`:6-15`)
A **fake** (a stand-in object that acts like the real thing but only records what happens). The real type is `fastapi.WebSocket`.
- `__init__` sets `accepted = False` and `messages = []` (`:7-9`).
- `async def accept()` sets `accepted = True` (`:11-12`). The real hub calls `await websocket.accept()` (`realtime_service.py:25`).
- `async def send_json(payload)` appends to `messages` (`:14-15`). The hub calls it in `publish` (`realtime_service.py:40`).
`async def` (a function that can pause while waiting, so other work runs. You call it with `await`).

### The test (`:18-40`)
`@pytest.mark.asyncio` (`:18`) tells the pytest-asyncio plugin to run this async test inside an event loop (the engine that runs async code). Without it pytest would not run it correctly.
1. `hub = RealtimeHub()`, `hub.bind_running_loop()` (`:20-21`) stores the current loop (`realtime_service.py:21-22`).
2. Two fake sockets are made (`:22-23`).
3. `await hub.connect('passenger:1:ride:7', passenger_socket)` (`:25`) accepts the socket and files it under that **channel** (a named room; only sockets in the room get its messages). Same for `'passenger:2:ride:8'` (`:26`). `# type: ignore[arg-type]` silences the type checker because the fake is not a real `WebSocket`.
4. `await hub.publish('passenger:1:ride:7', {...})` (`:27-30`) sends a message to that channel only.
5. Asserts: passenger socket was accepted, got exactly that message, and the other socket got nothing (`:32-36`).
6. `hub.disconnect(...)` (`:38`) removes the socket. A second `publish` (`:39`) must not reach it, so it still has 1 message (`:40`).

## 4. How data flows
```
test --connect--> hub._connections['passenger:1:ride:7'] = {fake1}
test --publish(channel, msg)--> hub --send_json--> fake1.messages [msg]
                                (fake2 is in another channel: nothing)
test --disconnect--> hub removes fake1 --publish--> nobody receives
```

## 5. Try it
```zsh
cd backend
uv run pytest tests/unit/test_realtime_service.py -v
```
Expected: `1 passed`. This needs the `pytest-asyncio` dev dependency (listed in `pyproject.toml`).

## 6. Can it be better?
- Good: proves channel isolation and clean disconnect, with no network.
- Weak: does not test a socket that raises an error on send (the hub removes such "stale" sockets, `realtime_service.py:38-44`), nor `publish_from_request` or offer expiry.
- Cleaner way (opinion): add a `BrokenSocket` whose `send_json` raises, then assert it is dropped.
- Security: channel names contain user ids; the real route must check who may join a channel (not tested here).

## 7. Check yourself
1. Why does the other socket receive no message?
2. What does `@pytest.mark.asyncio` do, and what happens without it?
