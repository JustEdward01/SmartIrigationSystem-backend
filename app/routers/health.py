"""Healthcheck endpoint."""

from fastapi import APIRouter

from ..services import ml

router = APIRouter()


@router.get("/api/health")
async def health() -> dict[str, str]:
    """Return status of server and ML model."""
    model, _ = ml.load_model()
    return {"status": "ok", "ml_loaded": str(model is not None)}
