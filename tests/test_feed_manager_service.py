import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from service.feed_manager import RssAtomFeeds


@pytest.mark.asyncio
async def test_register_feed_adds_task():
    manager = RssAtomFeeds()

    with patch.object(manager, "_ensure_session", new=AsyncMock()), \
         patch.object(manager, "_poll_feed", new=AsyncMock()):

        await manager.register_feed("http://example.com")

        assert "http://example.com" in manager._tasks


@pytest.mark.asyncio
async def test_register_feed_duplicate():
    manager = RssAtomFeeds()

    with patch.object(manager, "_ensure_session", new=AsyncMock()), \
         patch.object(manager, "_poll_feed", new=AsyncMock()):

        await manager.register_feed("http://example.com")
        await manager.register_feed("http://example.com")

        # Should not create duplicate tasks
        assert len(manager._tasks) == 1


@pytest.mark.asyncio
async def test_deregister_feed_success():
    manager = RssAtomFeeds()

    async def dummy_task():
        await asyncio.sleep(10)

    task = asyncio.create_task(dummy_task())
    manager._tasks["http://example.com"] = task
    manager._latest_ids["http://example.com"] = "123"

    await manager.deregister_feed("http://example.com")

    assert "http://example.com" not in manager._tasks


@pytest.mark.asyncio
async def test_deregister_feed_not_found():
    manager = RssAtomFeeds()

    with pytest.raises(ValueError):
        await manager.deregister_feed("http://not-registered.com")


@pytest.mark.asyncio
async def test_shutdown_calls_deregister():
    manager = RssAtomFeeds()

    with patch.object(manager, "deregister_feed", new=AsyncMock()), \
         patch.object(manager, "_close_session", new=AsyncMock()):

        manager._tasks = {"a": None, "b": None}

        await manager.shutdown()

        assert manager.deregister_feed.call_count == 2