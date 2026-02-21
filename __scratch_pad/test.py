import asyncio
import aiohttp
import feedparser
import random
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

FEEDS = [
    "https://status.openai.com/feed.rss",
    "https://status.openai.com/feed.atom"
]

BASE_INTERVAL = 60
MAX_BACKOFF = 600
REQUEST_TIMEOUT = 10

console = Console()
latest_ids = {url: None for url in FEEDS}


async def poll_feed(session, url):
    interval = BASE_INTERVAL

    while True:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")
                raw = await resp.read()

            feed = feedparser.parse(raw)

            if feed.entries:
                entry = feed.entries[0]
                entry_id = entry.get("id") or entry.get("guid") or entry.get("link")

                if latest_ids[url] != entry_id:
                    latest_ids[url] = entry_id

                    title = entry.get("title", "No title")
                    summary = entry.get("summary", "")

                    panel = Panel(
                        Markdown(summary),
                        title=f"[bold]{title}[/bold]",
                        subtitle=url,
                        expand=False
                    )

                    console.print()
                    console.print(panel)

                    interval = BASE_INTERVAL
                else:
                    interval = min(interval * 2, MAX_BACKOFF)
            else:
                interval = min(interval * 2, MAX_BACKOFF)

        except Exception as e:
            console.print(f"[red]Error polling {url}: {e}[/red]")
            interval = min(interval * 2, MAX_BACKOFF)

        await asyncio.sleep(random.uniform(0, interval))


async def main():
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await asyncio.gather(*(poll_feed(session, url) for url in FEEDS))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped.[/yellow]")