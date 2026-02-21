import feedparser
import asyncio
import random

from datetime import datetime
from typing import Dict, Optional, Any
from aiohttp import ClientSession, ClientTimeout, ClientResponse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from model.feed_manager import FeedManger


class RssAtomFeeds(FeedManger):
    """
    Concrete implementation of FeedManger.

    Uses asyncio-based polling with aiohttp for HTTP requests
    and feedparser for RSS/Atom parsing.

    Singleton behavior is inherited from FeedManger.
    """

    BASE_INTERVAL: int = 5
    MAX_BACKOFF: int = 600
    REQUEST_TIMEOUT: int = 10

    def __init__(self) -> None:
        """
        Initialize internal state (singleton-safe).
        """
        if hasattr(self, "_initialized"):
            return

        self._console: Console = Console()
        self._session: Optional[ClientSession] = None
        self._tasks: Dict[str, asyncio.Task[None]] = {}
        self._latest_ids: Dict[str, Optional[str]] = {}

        self._initialized: bool = True

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    async def register_feed(self, url: str) -> None:
        """
        Register and start polling a feed.

        Args:
            url (str): RSS/Atom feed URL.
        """
        if url in self._tasks:
            self._log("Already monitoring", url, level="warning")
            return

        await self._ensure_session()

        self._latest_ids[url] = None
        task: asyncio.Task[None] = asyncio.create_task(self._poll_feed(url))
        self._tasks[url] = task

        self._log("Started monitoring", url, level="success")

    async def deregister_feed(self, url: str) -> None:
        """
        Stop polling a feed and cancel its task.

        Raises:
            ValueError: If feed is not currently registered.
        """
        if url not in self._tasks:
            raise ValueError(f"Feed not registered: {url}")

        task: asyncio.Task[None] = self._tasks.pop(url)
        self._latest_ids.pop(url, None)

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        self._log("Stopped monitoring", url, level="warning")

    async def shutdown(self) -> None:
        """
        Gracefully stop all feeds and close HTTP session.
        """
        await asyncio.gather(
            *(self.deregister_feed(url) for url in list(self._tasks.keys()))
        )
        await self._close_session()

    # ─────────────────────────────────────────────
    # Internal Lifecycle
    # ─────────────────────────────────────────────

    async def _ensure_session(self) -> None:
        """
        Lazily create aiohttp client session.
        """
        if self._session is None:
            timeout: ClientTimeout = ClientTimeout(total=self.REQUEST_TIMEOUT)
            self._session = ClientSession(timeout=timeout)

    async def _close_session(self) -> None:
        """
        Close aiohttp session if active.
        """
        if self._session is not None:
            await self._session.close()
            self._session = None

    # ─────────────────────────────────────────────
    # Poll Worker
    # ─────────────────────────────────────────────

    async def _poll_feed(self, url: str) -> None:
        """
        Continuously poll a feed with exponential backoff and jitter.

        Args:
            url (str): Feed URL.
        """
        assert self._session is not None

        interval: int = self.BASE_INTERVAL

        while True:
            try:
                async with self._session.get(url) as response:
                    response = response  # type: ClientResponse

                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status}")

                    raw: bytes = await response.read()

                parsed_feed: Any = feedparser.parse(raw)

                if parsed_feed.entries:
                    entry: dict = parsed_feed.entries[0]

                    entry_id: Optional[str] = (
                            entry.get("id")
                            or entry.get("guid")
                            or entry.get("link")
                    )

                    if self._latest_ids.get(url) != entry_id:
                        self._latest_ids[url] = entry_id
                        self._render_entry(url, entry)
                        interval = self.BASE_INTERVAL
                    else:
                        self._log("No updates", url, level="info")
                        interval = min(interval * 2, self.MAX_BACKOFF)

                else:
                    self._log("Feed returned no entries", url, level="info")
                    interval = min(interval * 2, self.MAX_BACKOFF)

            except asyncio.CancelledError:
                raise

            except Exception as exc:
                self._log(f"Error polling: {exc}", url, level="error")
                interval = min(interval * 2, self.MAX_BACKOFF)

            await asyncio.sleep(random.uniform(0, interval))

    # ─────────────────────────────────────────────
    # Rendering & Logging
    # ─────────────────────────────────────────────

    def _render_entry(self, url: str, entry: Dict[str, Any]) -> None:
        """
        Render a feed entry using Rich Panel.

        Args:
            url (str): Feed source URL.
            entry (Dict[str, Any]): Parsed entry dictionary.
        """
        title: str = str(entry.get("title", "No title"))
        summary: str = str(entry.get("summary", ""))

        panel: Panel = Panel(
            Markdown(summary),
            title=f"[bold]{title}[/bold]",
            subtitle=url,
            expand=False,
        )

        self._console.print()
        self._console.print(panel)

    def _log(self, message: str, url: str, level: str = "info") -> None:
        """
        Print log message with human-readable timestamp.

        Args:
            message (str): Log message.
            url (str): Feed URL.
            level (str): Log level indicator.
        """
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        color_map: Dict[str, str] = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }

        color: str = color_map.get(level, "white")

        self._console.print(
            f"[{color}]{timestamp} | {message} | {url}[/{color}]"
        )


# ─────────────────────────────────────────────
# Example Runner
# ─────────────────────────────────────────────

async def main() -> None:
    """
    Standalone runner for manual testing.
    """
    manager: RssAtomFeeds = RssAtomFeeds()

    await manager.register_feed("https://status.openai.com/feed.rss")
    await manager.register_feed("https://status.openai.com/feed.atom")

    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
