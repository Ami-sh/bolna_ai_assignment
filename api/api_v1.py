from fastapi import APIRouter
from api.v1.health_probes.health import router as health_router
from api.v1.rss_atom_feeds import router as feeds_router
from api.v1.stream_console_out import router as stream_console_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(feeds_router, prefix="/feeds", tags=["Feeds"])
api_router.include_router(stream_console_router, prefix="/stream-console", tags=["Stream Console"])
