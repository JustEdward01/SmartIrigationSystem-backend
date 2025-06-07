import pandas as pd
from datetime import timedelta

def recommend_watering(model, row: dict, forecast_df: pd.DataFrame = None, moisture_threshold: float = 60.0) -> dict:
    """
    Primesti observație (dict cu cheile input_features).
    Returnează:
        - water_given_ml (float)
        - avoid_overwatering (bool)
        - next_watering_datetime (str)
    """
    timestamp = row.get("timestamp")
    input_row = row.copy()
    if "timestamp" in input_row:
        input_row.pop("timestamp")

    df = pd.DataFrame([input_row])
    preds = model.predict(df)[0]
    vol, next_days = float(preds[0]), float(preds[1])

    avoid = False
    if row['soil_moisture'] >= moisture_threshold or vol <= 0:
        avoid = True
        vol = 0.0

    if forecast_df is not None and timestamp is not None:
        today = pd.to_datetime(timestamp).date()
        mask = forecast_df['date'].dt.date == today
        if mask.any() and forecast_df.loc[mask, 'weather_outside'].iloc[0] == 'rainy':
            avoid = True
            vol = 0.0

    next_dt = pd.to_datetime(timestamp) + timedelta(days=next_days) if timestamp else None

    return {
        'water_given_ml': round(vol, 1),
        'avoid_overwatering': avoid,
        'next_watering_datetime': next_dt.strftime('%Y-%m-%d %H:%M') if next_dt is not None else None
    }
