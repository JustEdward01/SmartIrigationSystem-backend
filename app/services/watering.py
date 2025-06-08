"""Machine learning watering predictions."""

from __future__ import annotations

import joblib
import pandas as pd

from ..models.schemas import PredictRequest

multi_rf = None
plant_type_encoder = None


def _load_models() -> None:
    """Load sklearn models if not already loaded."""
    global multi_rf, plant_type_encoder
    if multi_rf is None or plant_type_encoder is None:
        multi_rf = joblib.load("smartplant_rf_model.joblib")
        plant_type_encoder = joblib.load("plant_type_encoder.joblib")


def predict(request: PredictRequest) -> tuple[float, float]:
    """Return water volume and next watering days using ML model."""
    _load_models()
    plant_onehot = plant_type_encoder.transform(
        pd.DataFrame([[request.plant_type]], columns=["plant_type"])
    )
    input_features = [
        request.soil_moisture,
        request.temperature,
        request.air_humidity,
        request.light,
        request.last_watered_days,
        request.ml_prediction_prev,
    ] + list(plant_onehot[0])
    columns = [
        "soil_moisture",
        "temperature",
        "air_humidity",
        "light",
        "last_watered_days",
        "ml_prediction_prev",
    ] + list(plant_type_encoder.get_feature_names_out(["plant_type"]))
    input_df = pd.DataFrame([input_features], columns=columns)
    water_given_ml, next_watering_days = multi_rf.predict(input_df)[0]
    return float(water_given_ml), float(next_watering_days)

