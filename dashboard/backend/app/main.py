from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.dashboard import router

app = FastAPI(title="Inside Sales Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
