from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_plant_info():
    resp = client.get("/api/plant-info?plant_type=tomato")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_predict_fallback():
    payload = {
        "soil_moisture": 20,
        "temperature": 25,
        "air_humidity": 50,
        "light": 1000,
        "last_watered_days": 2,
        "ml_prediction_prev": 0,
        "plant_type": "tomato"
    }
    resp = client.post("/predict", json=payload, headers={"x-api-key": "wrong"})
    assert resp.status_code == 403


def test_sensors_no_key():
    resp = client.get("/api/sensors")
    assert resp.status_code == 422
