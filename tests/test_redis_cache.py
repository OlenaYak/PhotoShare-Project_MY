import pytest
from unittest.mock import AsyncMock
from app.cache import redis_cache
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    class FakeRedis:
        storage = {}

        async def set(self, key, value):
            self.storage[key] = value

        async def get(self, key):
            value = self.storage.get(key, None)
            if value is not None:
                return value.encode()   
            return None

        async def ping(self):
            return True

    fake = FakeRedis()

    monkeypatch.setattr(redis_cache, "set", fake.set)
    monkeypatch.setattr(redis_cache, "get", fake.get)
    monkeypatch.setattr(redis_cache, "ping", fake.ping)

    return fake


@pytest.mark.asyncio
async def test_redis_ping(monkeypatch):
    ping_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(redis_cache, "ping", ping_mock)

    response = await redis_cache.ping()
    assert response is True
    ping_mock.assert_awaited_once()