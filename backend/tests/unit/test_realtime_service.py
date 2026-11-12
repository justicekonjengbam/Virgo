import pytest

from app.services.realtime_service import RealtimeHub


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[dict] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict) -> None:
        self.messages.append(payload)


@pytest.mark.asyncio
async def test_realtime_hub_delivers_to_connected_channel_only() -> None:
    hub = RealtimeHub()
    hub.bind_running_loop()
    passenger_socket = FakeWebSocket()
    other_socket = FakeWebSocket()

    await hub.connect('passenger:1:ride:7', passenger_socket)  # type: ignore[arg-type]
    await hub.connect('passenger:2:ride:8', other_socket)  # type: ignore[arg-type]
    await hub.publish(
        'passenger:1:ride:7',
        {'type': 'ride.status', 'data': {'status': 'driver_arriving'}},
    )

    assert passenger_socket.accepted
    assert passenger_socket.messages == [
        {'type': 'ride.status', 'data': {'status': 'driver_arriving'}},
    ]
    assert other_socket.messages == []

    hub.disconnect('passenger:1:ride:7', passenger_socket)  # type: ignore[arg-type]
    await hub.publish('passenger:1:ride:7', {'type': 'ride.status', 'data': {}})
    assert len(passenger_socket.messages) == 1
