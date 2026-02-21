from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.api_v1 import api_router as router



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup initiated.")

    print("Startup tasks completed successfully.")

    yield  # ---- App runs here ----

    print("Application shutdown initiated.")


app = FastAPI(
    title="bolna_ai_assessment",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")
