from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Input features for watering prediction."""

    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=-20, le=60)
    air_humidity: float = Field(..., ge=0, le=100)
    light: float = Field(..., ge=0)
    last_watered_days: float = Field(..., ge=0)
    ml_prediction_prev: float
    plant_type: str


class PlantInfo(BaseModel):
    """Data about a plant type."""

    plant_type: str
    description: str | None = None
    tratament: str | None = None

