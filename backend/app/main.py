from fastapi import FastAPI, Request

app = FastAPI()

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_msg = traceback.format_exc()
    logging.error(f"GLOBAL HANDLER: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "trace": error_msg.splitlines()[-3:]},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
import traceback
from fastapi import Request

# Setup File Logging
logging.basicConfig(filename='backend_debug.log', level=logging.INFO)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        body = await request.body()
        logging.info(f"REQ: {request.method} {request.url} BODY: {body.decode(errors='ignore')}")
        response = await call_next(request)
        return response
    except Exception as e:
        logging.error("UNHANDLED EXCEPTION:")
        logging.error(traceback.format_exc())
        raise e

# Include routers
from app.routers import notifications
from app.routers import payments
from app.routers import recurring
from app.routers import companies

app.include_router(notifications.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(recurring.router, prefix="/api")
app.include_router(companies.router, prefix="/api")

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
