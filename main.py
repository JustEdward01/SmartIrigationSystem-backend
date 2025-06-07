import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status, Header, Depends, Request, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import logging
import joblib
import pandas as pd
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from utils.symptom_action_map import SYMPTOM_ACTION_MAP
from datetime import datetime
import serial 
# ========== CONFIG ==========
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_SECRET = os.getenv("API_SECRET")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(filename='api.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )

# ====== ÎNCĂRCARE MODELE ======
multi_rf = joblib.load("smartplant_rf_model.joblib")
plant_type_encoder = joblib.load("plant_type_encoder.joblib")

MODEL_PATH = 'plant_diagnosis_final.keras'
LABEL_MAP_PATH = 'label_map.json'
PLANT_INFO_PATH = 'plant_info.json'
IMG_SIZE = (224, 224)

try:
    plant_model = tf.keras.models.load_model(MODEL_PATH)
    with open(LABEL_MAP_PATH) as f:
        plant_label_map = json.load(f)
    plant_index_to_class = {v: k for k, v in plant_label_map.items()}
    print("Model AI vizual încărcat OK")
except Exception as e:
    plant_model = None
    plant_label_map = None
    plant_index_to_class = None
    logging.error(f"Eroare la încărcarea modelului vizual: {e}")

def load_plant_info(plant_type=None):
    try:
        with open(PLANT_INFO_PATH, "r", encoding="utf-8") as f:
            info = json.load(f)
        if plant_type:
            return info.get(plant_type.lower(), None)
        return info
    except Exception as e:
        logging.error(f"Eroare la încărcarea plant_info.json: {e}")
        return None

# ========== ENDPOINTURI BACKEND ==========

@app.get("/api/plant-info")
def get_plant_info(plant_type: str = None):
    info = load_plant_info(plant_type)
    if not info:
        raise HTTPException(status_code=404, detail="Informații despre plantă negăsite.")
    return info

@app.post("/predict", dependencies=[Depends(verify_api_key)])
async def predict_watering(data: dict, request: Request):
    try:
        input_dict = data
        plant_onehot = plant_type_encoder.transform(
            pd.DataFrame([[input_dict["plant_type"]]], columns=['plant_type'])
        )
        input_features = [
            input_dict["soil_moisture"],
            input_dict["temperature"],
            input_dict["air_humidity"],
            input_dict["light"],
            input_dict["last_watered_days"],
            input_dict["ml_prediction_prev"],
        ] + list(plant_onehot[0])
        columns = [
            'soil_moisture', 'temperature', 'air_humidity', 'light',
            'last_watered_days', 'ml_prediction_prev'
        ] + list(plant_type_encoder.get_feature_names_out(['plant_type']))
        input_df = pd.DataFrame([input_features], columns=columns)
        y_pred = multi_rf.predict(input_df)[0]
        water_given_ml, next_watering_days = y_pred

        log_entry = {
            **input_dict,
            "water_given_ml": float(water_given_ml),
            "next_watering_days": float(next_watering_days)
        }
        supabase.table("watering_logs").insert(log_entry).execute()

        return {
            "water_given_ml": round(float(water_given_ml), 1),
            "next_watering_days": round(float(next_watering_days), 1),
            "explanation": [
                f"Model ML pentru planta: {input_dict['plant_type']}."
            ],
            "source": "ML"
        }
    except Exception as e:
        logging.error(f"Eroare la ML predict: {e}")
        fallback = {
            "water_given_ml": 80.0 if data["soil_moisture"] < 30 else 0.0,
            "next_watering_days": 1 if data["soil_moisture"] < 30 else 3,
            "explanation": ["Fallback: ML nu a răspuns. Decizie bazată doar pe prag umiditate."],
            "source": "fallback"
        }
        return fallback

@app.get("/history")
def get_history(limit: int = 20):
    try:
        response = supabase.table("sensor_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        logging.info("History request - success")
        return response.data
    except Exception as e:
        logging.error(f"Eroare la history: {e}")
        raise HTTPException(status_code=500, detail="Eroare la interogare istoric")

@app.get("/api/history")
def get_watering_history(limit: int = 100):
    try:
        response = supabase.table("watering_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        logging.info("Watering history request - success")
        return response.data
    except Exception as e:
        logging.error(f"Eroare la watering_history: {e}")
        raise HTTPException(status_code=500, detail="Eroare la interogare istoric udări")

@app.get("/api/sensors", dependencies=[Depends(verify_api_key)])
async def get_sensors():
    try:
        response = supabase.table("sensor_logs").select("*").order("timestamp", desc=True).limit(1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="No sensor data")
        data = response.data[0]
        return {
            "soil_moisture": data.get("soil_moisture", 0.0),
            "temperature": data.get("temperature", 0.0),
            "air_humidity": data.get("air_humidity", 0.0),
            "light": data.get("light", 0.0),
            "plant_type": data.get("plant_type", "unknown"),
            "last_watered_days": data.get("last_watered_days", 0.0),
            "ml_prediction_prev": data.get("ml_prediction_prev", 0.0),
            "timestamp": data.get("timestamp", "")
        }
    except Exception as e:
        logging.error(f"Eroare la sensors: {e}")
        raise HTTPException(status_code=500, detail="Eroare la interogare senzori")

@app.post("/api/diagnose-photo", dependencies=[Depends(verify_api_key)])
async def diagnose_photo(file: UploadFile = File(...), plant_type: str = None):
    try:
        if plant_model is None or plant_index_to_class is None:
            raise HTTPException(status_code=500, detail="Modelul AI nu este încărcat.")

        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img = img.resize(IMG_SIZE)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = plant_model.predict(img_array)
        pred_index = int(np.argmax(preds))
        confidence = float(np.max(preds))
        predicted_class = plant_index_to_class[pred_index]

        mapping = SYMPTOM_ACTION_MAP.get(predicted_class, SYMPTOM_ACTION_MAP["unknown"])
        adjust_days = mapping["adjust_watering_days"]
        reduce_ml = mapping["reduce_water_ml"]
        decision_reason = f"Ajustare automată: detectat simptom '{predicted_class}' cu scor {confidence:.2f}. {mapping['notify_user']}"

        log_entry = {
            "plant_type": plant_type,
            "img_path": None,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "action_message": mapping["notify_user"],
            "adjust_days": adjust_days,
            "reduce_ml": reduce_ml,
            "all_scores": {plant_index_to_class[i]: float(score) for i, score in enumerate(preds[0])},
            "decision_reason": decision_reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            supabase.table("diagnostic_logs").insert(log_entry).execute()
        except Exception as db_err:
            logging.error(f"Eroare la logare diagnostic_logs: {db_err}")

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "all_scores": {plant_index_to_class[i]: float(score) for i, score in enumerate(preds[0])},
            "action_message": mapping["notify_user"],
            "adjust_days": adjust_days,
            "reduce_ml": reduce_ml,
            "decision_reason": decision_reason
        }
    except Exception as e:
        logging.error(f"Eroare la diagnose-photo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diagnostic-logs")
async def get_diagnostic_logs(limit: int = 50):
    try:
        response = supabase.table("diagnostic_logs") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
    except Exception as e:
        logging.error(f"Eroare la get_diagnostic_logs: {e}")
        raise HTTPException(status_code=500, detail="Eroare la interogare diagnostic logs")

@app.patch("/api/diagnostic-logs/{log_id}/feedback")
async def update_diagnostic_feedback(log_id: str, user_feedback: str = Body(..., embed=True)):
    try:
        response = supabase.table("diagnostic_logs") \
            .update({"user_feedback": user_feedback}) \
            .eq("id", log_id) \
            .execute()
        if response.data:
            return {"message": "Feedback salvat", "log": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail="Log not found")
    except Exception as e:
        logging.error(f"Eroare la update_diagnostic_feedback: {e}")
        raise HTTPException(status_code=500, detail="Eroare la update feedback")

@app.post("/api/sensor-data")
async def receive_sensor_data(data: dict):
    print("RECEIVED DATA:", data)
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
    except Exception as e:
        print("EXCEPTION:", e)
        raise HTTPException(status_code=500, detail=f"Eroare la salvare date senzori: {e}")

# ===== Udare manuală =====

water_now_manual = False

@app.post("/api/manual-water")
async def trigger_manual_water():
    global water_now_manual
    water_now_manual = True
    return {"status": "manual_watering_requested"}

@app.get("/api/manual-water-status")
async def manual_water_status():
    global water_now_manual
    return {"water_now_manual": water_now_manual}

@app.post("/api/manual-water-done")
async def manual_water_done():
    global water_now_manual
    water_now_manual = False
    return {"status": "manual_watering_reset"}
class WiFiCreds(BaseModel):
    ssid: str
    password: str
@app.post("/set-wifi")
async def set_wifi(creds: WiFiCreds):
    try:
        # Trimite peste UART (sau API esp32 local, dacă rulezi pe aceeași rețea)
        ser = serial.Serial('COMx', 115200, timeout=1)  # înlocuiește COMx
        cmd = f"{creds.ssid},{creds.password}\n"
        ser.write(cmd.encode())
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
        
@app.get("/api/system-status")
def system_status():
    import socket
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return {
            "connected": True,
            "ssid": os.getenv("WIFI_SSID", "Unknown"),
            "ip": ip
        }
    except:
        return { "connected": False }
