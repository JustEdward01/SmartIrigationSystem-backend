"""Utility functions for image-based diagnostics."""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_PATH = Path("plant_diagnosis_final.keras")
LABEL_MAP_PATH = Path("label_map.json")
IMG_SIZE = (224, 224)

_model: tf.keras.Model | None = None
_index_to_class: dict[int, str] | None = None


def load_model() -> tuple[tf.keras.Model | None, dict[int, str] | None]:
    """Load the visual ML model lazily."""
    global _model, _index_to_class
    if _model is not None and _index_to_class is not None:
        return _model, _index_to_class
    try:
        _model = tf.keras.models.load_model(MODEL_PATH)
        with LABEL_MAP_PATH.open() as f:
            label_map = json.load(f)
        _index_to_class = {v: k for k, v in label_map.items()}
        logging.info("Loaded visual model")
    except Exception as exc:  # pragma: no cover - runtime errors
        logging.error("Failed loading model: %s", exc)
        _model, _index_to_class = None, None
    return _model, _index_to_class


def predict(image_bytes: bytes) -> Tuple[str, float, dict[str, float]]:
    """Predict plant symptom from an uploaded image."""
    model, idx_to_class = load_model()
    if model is None or idx_to_class is None:
        raise RuntimeError("Model not available")

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(IMG_SIZE)
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
    preds = model.predict(img_array)
    pred_index = int(np.argmax(preds))
    confidence = float(np.max(preds))
    predicted_class = idx_to_class[pred_index]
    scores = {idx_to_class[i]: float(score) for i, score in enumerate(preds[0])}
    return predicted_class, confidence, scores

