import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RealtimeHub:
    """Low-latency, process-local WebSocket fan-out for ride events.

    Cloud deployments must run one API process unless this hub is later backed by
    Redis pub/sub. Database state remains authoritative, so reconnecting clients
    always receive a fresh snapshot.
    """

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._expiry_tasks: dict[int, asyncio.Task[None]] = {}

    def bind_running_loop(self) -> None:
        self._loop = asyncio.get_running_loop()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[channel].add(websocket)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        connections = self._connections.get(channel)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(channel, None)

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in tuple(self._connections.get(channel, ())):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(channel, websocket)

    def publish_from_request(self, channel: str, payload: dict[str, Any]) -> None:
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.publish(channel, payload), self._loop)

    def schedule_offer_expiry(self, offer_id: int, delay_seconds: float) -> None:
        if not self._loop or not self._loop.is_running():
            return

        def schedule() -> None:
            previous = self._expiry_tasks.pop(offer_id, None)
            if previous:
                previous.cancel()
            self._expiry_tasks[offer_id] = asyncio.create_task(
                self._expire_offer(offer_id, max(0.0, delay_seconds)),
            )

        self._loop.call_soon_threadsafe(schedule)

    async def _expire_offer(self, offer_id: int, delay_seconds: float) -> None:
        try:
            await asyncio.sleep(delay_seconds)
            from app.services.realtime_events import expire_offer_and_publish

            await asyncio.to_thread(expire_offer_and_publish, offer_id)
        finally:
            self._expiry_tasks.pop(offer_id, None)


realtime_hub = RealtimeHub()
