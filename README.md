# SmartPlant Backend

Backend FastAPI pentru sistemul SmartPlant (udare automată).

## Cum pornești local

1. Instalează dependențele:
   pip install -r requirements.txt

2. Rulează serverul local:
   uvicorn app.main:app --reload

Accesează: http://localhost:8000

## Testare rapidă cu Postman sau curl
- GET `/` — health check
- POST `/predict` — cu un payload JSON

### ATENȚIE
Copiază modelul tău ML `watering_multioutput_sklearn.pkl` în `app/ml/`
