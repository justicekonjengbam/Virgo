import time
from collections import defaultdict
from threading import Lock
from typing import Callable

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._history: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            entries = self._history[key]
            # Prune expired timestamps
            recent = [t for t in entries if t > cutoff]
            if len(recent) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - recent[0])) + 1)
                self._history[key] = recent
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Please wait {retry_after} seconds before trying again.",
                    headers={"Retry-After": str(retry_after)},
                )
            recent.append(now)
            self._history[key] = recent

    def clear(self) -> None:
        with self._lock:
            self._history.clear()


# Pre-configured rate limiters for authentication endpoints
# 10 OTP requests per minute per client IP
otp_request_limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)
# 15 OTP verification attempts per minute per client IP
otp_verify_limiter = SlidingWindowRateLimiter(limit=15, window_seconds=60)
# 15 login attempts per minute per client IP
login_limiter = SlidingWindowRateLimiter(limit=15, window_seconds=60)


def client_identifier(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def rate_limit(limiter: SlidingWindowRateLimiter, key_prefix: str = "") -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        ip = client_identifier(request)
        key = f"{key_prefix}:{ip}" if key_prefix else ip
        limiter.check(key)

    return dependency

