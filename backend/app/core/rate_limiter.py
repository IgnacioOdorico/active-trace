import asyncio
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_rate_limited(self, key: str) -> bool:
        async with self._lock:
            now = time.time()
            window_start = now - self._window_seconds
            self._attempts[key] = [t for t in self._attempts[key] if t > window_start]
            return len(self._attempts[key]) >= self._max_attempts

    async def record_attempt(self, key: str) -> None:
        async with self._lock:
            self._attempts[key].append(time.time())

    async def clear(self, key: str) -> None:
        async with self._lock:
            self._attempts.pop(key, None)


rate_limiter = RateLimiter()
