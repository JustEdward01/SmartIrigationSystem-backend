"""Sensor data and history endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..utils.db import client as supabase
from ..utils.security import verify_api_key

router = APIRouter()


@router.get("/history")
def get_history(limit: int = 20):
    """Return recent sensor history entries."""
    try:
        response = (
            supabase.table("sensor_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        )
        return response.data
    except Exception as exc:  # pragma: no cover - db failures
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/history")
def get_watering_history(limit: int = 100):
    """Return watering logs."""
    try:
        response = (
            supabase.table("watering_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        )
        return response.data
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/sensors", dependencies=[Depends(verify_api_key)])
async def get_sensors():
    """Return latest sensor values."""
    try:
        response = (
            supabase.table("sensor_logs").select("*").order("timestamp", desc=True).limit(1).execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="No sensor data")
        return response.data[0]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/api/sensor-data")
async def receive_sensor_data(data: dict):
    """Store incoming sensor measurements from ESP32."""
    try:
        db_data = {
            "plant_type": data.get("plant_type"),
            "soil_moisture": data.get("soil_moisture"),
            "temperature": data.get("temperature"),
            "air_humidity": data.get("air_humidity"),
            "light": data.get("light"),
        }
        supabase.table("sensor_logs").insert(db_data).execute()
        water_now = data.get("soil_moisture", 100) < 35
        return {"water_now": water_now}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))

