from fastapi import FastAPI

app = FastAPI()

# Include routers
from app.routers import notifications

app.include_router(notifications.router, prefix="/api")

# Startup event - Initialize scheduler
@app.on_event("startup")
def startup_event():
        """Initialize APScheduler on application startup."""
        from app.scheduler import start_scheduler
        start_scheduler()

# Shutdown event - Cleanup scheduler
@app.on_event("shutdown")
def shutdown_event():
        """Cleanup APScheduler on application shutdown."""
        from app.scheduler import shutdown_scheduler
        shutdown_scheduler()


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "controlgastos API"
    }
