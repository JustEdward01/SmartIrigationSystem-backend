"""Image diagnosis and diagnostic logs."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Body

from ..services import ml
from ..utils.db import client as supabase
from ..utils.security import verify_api_key
from utils.symptom_action_map import SYMPTOM_ACTION_MAP

router = APIRouter()


@router.post("/api/diagnose-photo", dependencies=[Depends(verify_api_key)])
async def diagnose_photo(file: UploadFile = File(...), plant_type: str | None = None):
    """Diagnose a plant photo using the ML model."""
    try:
        contents = await file.read()
        predicted_class, confidence, scores = ml.predict(contents)
        mapping = SYMPTOM_ACTION_MAP.get(predicted_class, SYMPTOM_ACTION_MAP["unknown"])
        adjust_days = mapping["adjust_watering_days"]
        reduce_ml = mapping["reduce_water_ml"]
        decision_reason = (
            f"Detectat '{predicted_class}' cu scor {confidence:.2f}. {mapping['notify_user']}"
        )
        log_entry = {
            "plant_type": plant_type,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "action_message": mapping["notify_user"],
            "adjust_days": adjust_days,
            "reduce_ml": reduce_ml,
            "all_scores": scores,
            "decision_reason": decision_reason,
        }
        try:
            supabase.table("diagnostic_logs").insert(log_entry).execute()
        except Exception as db_err:  # pragma: no cover - db error
            import logging

            logging.error("diagnostic_logs insert failed: %s", db_err)
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "all_scores": scores,
            "action_message": mapping["notify_user"],
            "adjust_days": adjust_days,
            "reduce_ml": reduce_ml,
            "decision_reason": decision_reason,
        }
    except Exception as exc:  # pragma: no cover - runtime errors
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/diagnostic-logs")
async def get_diagnostic_logs(limit: int = 50):
    """Return saved diagnostic logs."""
    try:
        response = (
            supabase.table("diagnostic_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        )
        return response.data
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.patch("/api/diagnostic-logs/{log_id}/feedback")
async def update_diagnostic_feedback(log_id: str, user_feedback: str = Body(..., embed=True)):
    """Store user feedback for a diagnostic log."""
    try:
        response = (
            supabase.table("diagnostic_logs").update({"user_feedback": user_feedback}).eq("id", log_id).execute()
        )
        if response.data:
            return {"message": "Feedback saved", "log": response.data[0]}
        raise HTTPException(status_code=404, detail="Log not found")
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))

