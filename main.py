"""FastAPI application entry-point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    plant_router,
    sensor_router,
    diagnostics_router,
    manual_router,
    system_router,
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

