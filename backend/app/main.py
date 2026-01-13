from fastapi import FastAPI

app = FastAPI()

# Include routers
from app.routers import notifications

app.include_router(notifications.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "controlgastos API"
    }
