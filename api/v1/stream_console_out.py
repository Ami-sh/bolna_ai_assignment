import sys
import asyncio
from fastapi import FastAPI, APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="", tags=["feeds"])

# Async queue to store log lines
LOG_QUEUE = asyncio.Queue()


# Custom stdout interceptor
class StdoutInterceptor:
    def __init__(self):
        self._stdout = sys.__stdout__  # original stdout

    def write(self, message):
        if message.strip():
            try:
                # Push message into queue (non-blocking)
                asyncio.get_event_loop().call_soon_threadsafe(
                    LOG_QUEUE.put_nowait, message.strip()
                )
            except RuntimeError:
                # event loop not ready yet
                pass

        # Still write to actual stdout (Railway logs)
        self._stdout.write(message)

    def flush(self):
        self._stdout.flush()


# Replace stdout globally
sys.stdout = StdoutInterceptor()


@router.get("/logs")
async def stream_logs():
    async def event_generator():
        while True:
            log = await LOG_QUEUE.get()
            yield {"data": log}

    return EventSourceResponse(event_generator())