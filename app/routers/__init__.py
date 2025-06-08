"""Routers used by the FastAPI application."""

from .plant import router as plant_router
from .sensor import router as sensor_router
from .diagnostics import router as diagnostics_router
from .manual import router as manual_router
from .system import router as system_router
from .health import router as health_router

__all__ = [
    "plant_router",
    "sensor_router",
    "diagnostics_router",
    "manual_router",
    "system_router",
    "health_router",
]

