"""FastAPI application entry-point."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    plant_router,
    sensor_router,
    diagnostics_router,
    manual_router,
    system_router,
    health_router,
)
from app.utils.logging_config import setup_logging
from app.utils.middleware import RequestLoggerMiddleware

setup_logging()

app = FastAPI(title="SmartPlant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggerMiddleware)

app.include_router(plant_router)
app.include_router(sensor_router)
app.include_router(diagnostics_router)
app.include_router(manual_router)
app.include_router(system_router)
app.include_router(health_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return JSON error."""
    import logging

    logging.error("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

