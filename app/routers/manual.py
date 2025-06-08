"""Manual watering control endpoints."""

from fastapi import APIRouter

router = APIRouter()

water_now_manual = False


@router.post("/api/manual-water")
async def trigger_manual_water():
    """Request watering from the device."""
    global water_now_manual
    water_now_manual = True
    return {"status": "manual_watering_requested"}


@router.get("/api/manual-water-status")
async def manual_water_status():
    """Return current manual watering status."""
    return {"water_now_manual": water_now_manual}


@router.post("/api/manual-water-done")
async def manual_water_done():
    """Reset manual watering flag."""
    global water_now_manual
    water_now_manual = False
    return {"status": "manual_watering_reset"}

