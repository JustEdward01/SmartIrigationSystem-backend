# SmartPlant Backend

Backend FastAPI pentru sistemul SmartPlant (udare automată).

[![CI](https://github.com/yourusername/SmartIrigationSystem-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/SmartIrigationSystem-backend/actions/workflows/ci.yml)

## Cum pornești local

1. Instalează dependențele:
   `./scripts/setup_dev_env.sh`

2. Rulează serverul local:
   `uvicorn main:app --reload`

Accesează: http://localhost:8000

## Testare rapidă cu Postman sau curl
- GET `/` — health check
- POST `/predict` — cu un payload JSON

### ATENȚIE
Copiază modelul tău ML `watering_multioutput_sklearn.pkl` în `app/ml/`

## Docker

Pentru rulare în containere:

```bash
docker-compose up --build
```

## Firmware ESP32

Instrucțiunile pentru configurarea și uploadul firmware-ului se găsesc în [esp32/README.md](esp32/README.md).
