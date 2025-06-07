from pydantic import BaseModel, Field, validator
from datetime import datetime

class SensorLog(BaseModel):
    timestamp: datetime

    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=-20, le=60)
    air_humidity: float = Field(..., ge=0, le=100)
    light: float = Field(..., ge=0)
    last_watered_days: float = Field(..., ge=0)
    ml_prediction_prev: float = Field(..., ge=0)
    plant_type: str  # ex: "cactus", "ficus", "rosie", "busuioc"

    @validator('timestamp')
    def timestamp_cannot_be_future(cls, v):
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v > now:
            raise ValueError("Timestamp nu poate fi din viitor")
        return v
