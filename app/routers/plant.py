"""Plant related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from ..models.schemas import PredictRequest
from ..services import watering
from ..utils.loaders import load_plant_info
from ..utils.security import verify_api_key

router = APIRouter()


@router.get("/api/plant-info")
def get_plant_info(plant_type: str | None = None):
    """Return information about a plant type."""
    info = load_plant_info(plant_type)
    if not info:
        raise HTTPException(status_code=404, detail="Plant info not found")
    return info


@router.post("/predict", dependencies=[Depends(verify_api_key)])
def predict_watering(req: PredictRequest):
    """Predict watering volume and next watering date."""
    try:
        water_ml, next_days = watering.predict(req)
        return {
            "water_given_ml": round(water_ml, 1),
            "next_watering_days": round(next_days, 1),
            "source": "ML",
        }
    except Exception as exc:
        # Fallback simple heuristic
        fallback = {
            "water_given_ml": 80.0 if req.soil_moisture < 30 else 0.0,
            "next_watering_days": 1 if req.soil_moisture < 30 else 3,
            "source": "fallback",
        }
        logging = __import__("logging")
        logging.error("ML prediction failed: %s", exc)
        return fallback
