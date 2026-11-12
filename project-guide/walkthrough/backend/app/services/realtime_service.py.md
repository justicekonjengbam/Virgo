# backend/app/services/realtime_service.py

## 1. Purpose
This file is the **WebSocket hub**. A **WebSocket** (a long-lived two-way connection between app and server; unlike normal HTTP, the server can push messages any time. *Example:* a chat app). The hub keeps a list of connected clients per "channel" and sends them JSON. It also schedules the 30-second ride-offer timeout. `realtime_events.py` calls it; the WebSocket routes in `backend/app/api/` call `connect`/`disconnect`.

## 2. Imports, one by one
- `import asyncio` (line 1). Python's standard library for async code (**async** = code that can pause while waiting, so one thread serves many clients. *Example:* `await asyncio.sleep(2)`). Used for the event loop, tasks and sleep.
- `from collections import defaultdict` (line 2). A dict that creates a default value for missing keys. *Example:* `d = defaultdict(set); d['a'].add(1)` works without setup.
- `from typing import Any` (line 3). A type hint meaning "any value".
- `from fastapi import WebSocket` (line 5). The FastAPI object for one WebSocket connection. *Example:* `await ws.send_json({"a":1})`.

## 3. Walk through the code, top to bottom
### `class RealtimeHub` (lines 8-71)
The docstring (lines 9-14) warns: the hub lives in one process only. With two server processes, a client on process A would not hear events from process B. Redis pub/sub would fix it.

`__init__` (16-19): `_connections` maps channel name to a set of sockets (like `{'driver:5': {ws1}}`). `_loop` is the running event loop (the engine that runs async code), unknown at start. `_expiry_tasks` maps offer id to its timer task.

`bind_running_loop` (21-22): `asyncio.get_running_loop()` returns the current loop. Must be called from inside async code (probably app startup in `main.py`; check with `rg -n bind_running_loop backend`). Why: normal (sync) route functions run in other threads and need this loop to push messages.

`connect` (24-26): `await websocket.accept()` finishes the handshake, then adds the socket to the channel set.

`disconnect` (28-34): removes the socket; if the channel is empty, deletes the channel key. `.get` returns `None` if missing, so no error.

`publish` (36-44), async: loops over a `tuple(...)` copy (so the set can change during the loop). `await websocket.send_json(payload)` sends. On any error, the socket is marked stale and removed after the loop.

`publish_from_request` (46-48): a normal function that can be called from sync code. `asyncio.run_coroutine_threadsafe(coro, loop)` runs the async `publish` on the loop from another thread. It does nothing if there is no running loop. It does not wait for the result.

`schedule_offer_expiry` (50-62): returns if no loop. Defines inner `schedule()` which cancels any older timer for the same offer, then `asyncio.create_task(...)` starts `_expire_offer`. `call_soon_threadsafe(schedule)` runs `schedule` on the loop thread (tasks must be created there).

`_expire_offer` (64-71): sleeps `delay_seconds`, then imports `expire_offer_and_publish` inside the function (a **local import**, to avoid a circular import: `realtime_events.py` imports this file). `asyncio.to_thread(func, arg)` runs a blocking function in a worker thread so the loop is not frozen (it uses the database). `finally` always removes the task from the dict.

### `realtime_hub = RealtimeHub()` (line 74)
One shared instance (a **singleton**: one object everyone imports).

## 4. How data flows
```
Sync route (thread) -> realtime_events.publish_x -> hub.publish_from_request
   -> run_coroutine_threadsafe -> event loop -> publish -> ws.send_json -> App
Offer timer: schedule_offer_expiry -> loop -> sleep 30s -> to_thread(expire_offer_and_publish)
```

## 5. Try it
Not directly runnable (needs a running app). To watch it: run the backend, connect with `uvx websockets ws://127.0.0.1:8000/<ws-route>` (find the route with `rg -n "websocket" backend/app/api`).

## 6. Can it be better?
- Good: clear docstring about the one-process limit; stale sockets are cleaned.
- Weak: `except Exception` (line 41) hides real bugs. Timers are lost if the server restarts (pending offers then expire only when someone reads them; see `current_offer`). Sockets are sent one by one, so one slow client delays others. No auth inside the hub (routes must do it).
- Cleaner: use Redis pub/sub before running two processes. Use `asyncio.gather` to send in parallel.
- Security: channel names contain ids, so the WebSocket route must check the user owns the channel.

## 7. Check yourself
1. Why does `publish_from_request` use `run_coroutine_threadsafe`?
2. Why is `expire_offer_and_publish` imported inside `_expire_offer`?
