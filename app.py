# app.py
import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import xgboost as xgb
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

MODEL_DIR = os.environ.get("MODEL_DIR", "models")  # in Docker you'll copy model/ here
MODEL_FILE = os.path.join(MODEL_DIR, "xgb_booster.json")
FEATURE_FILE = os.path.join(MODEL_DIR, "feature_names.json")
META_FILE = os.path.join(MODEL_DIR, "model_metadata.json")
LOG_FILE = os.environ.get("REQUEST_LOG", "/tmp/request_log.csv")  # optional

# Load model + metadata at startup
if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(f"Model file not found at {MODEL_FILE}. Put model files in {MODEL_DIR}/")

booster = xgb.Booster()
booster.load_model(MODEL_FILE)

with open(FEATURE_FILE, "r") as f:
    feature_names = json.load(f)

with open(META_FILE, "r") as f:
    metadata = json.load(f)

THRESHOLD = float(metadata.get("threshold", 0.5))

# fastapi app
app = FastAPI(title="Breast-Risk API", version="1.0")

# allow CORS from any origin (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # limit this to your frontend origin in production
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    # Expect a dict mapping feature_name -> coded int/float
    data: Dict[str, Any]

class PredictResponse(BaseModel):
    probability: float
    label: int
    threshold: float
    confidence: float   # confidence of chosen class
    feature_order: list

def _prepare_input_dict(d: Dict[str, Any]):
    """
    Build a row (1 x n_features) in the exact feature order expected by the model.
    Missing features are filled with 0. Caller must ensure they supply the coded names.
    """
    row = []
    for fn in feature_names:
        # accept int/float strings, cast to float
        val = d.get(fn, None)
        if val is None:
            # if frontend didn't send a feature, treat as zero (or raise)
            row.append(0.0)
        else:
            try:
                row.append(float(val))
            except Exception:
                raise ValueError(f"Feature {fn} could not be parsed as float: {val}")
    return np.array(row, dtype=float).reshape(1, -1)

def _log_request(req_data: Dict[str, Any], prob: float, label: int):
    # Append a simple CSV line: timestamp,prob,label,keys...
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        header = False
        if not os.path.exists(LOG_FILE):
            header = True
        with open(LOG_FILE, "a") as f:
            if header:
                f.write("timestamp,prob,label,threshold\n")
            f.write(f"{datetime.utcnow().isoformat()},{prob:.6f},{label},{THRESHOLD}\n")
    except Exception:
        pass  # logging must not break prediction

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "threshold": THRESHOLD, "feature_count": len(feature_names)}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Validate incoming keys are subset of feature_names
    input_keys = set(req.data.keys())
    unknown = input_keys.difference(set(feature_names))
    if unknown:
        # not fatal but warn user
        # we return 400 to force the frontend to send correct keys
        raise HTTPException(status_code=400, detail=f"Unknown features in request: {sorted(list(unknown))}")

    try:
        x = _prepare_input_dict(req.data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    dm = xgb.DMatrix(x, feature_names=feature_names)
    prob = float(booster.predict(dm)[0])
    label = int(prob >= THRESHOLD)
    confidence = prob if label == 1 else (1.0 - prob)

    # log request asynchronously-ish (best-effort)
    _log_request(req.data, prob, label)

    return {
        "probability": prob,
        "label": label,
        "threshold": THRESHOLD,
        "confidence": confidence,
        "feature_order": feature_names
    }
