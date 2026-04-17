from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np

app = FastAPI(title="IDS Classification API")

try:
    model = joblib.load('rf_model.joblib')
    scaler = joblib.load('scaler.joblib')
    features = joblib.load('features.joblib')
except Exception as e:
    print(f"Warning: Model artifacts not found. Please run train.py first. Error: {e}")
    model, scaler, features = None, None, None

class TrafficData(BaseModel):
    data: list[dict]

@app.post("/analyze-traffic")
def analyze_traffic(payload: TrafficData):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    df = pd.DataFrame(payload.data)
    
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing_cols}")
        
    X = df[features]
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(0, inplace=True)
    
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    results = []
    for pred, prob in zip(predictions, probabilities):
        classification = "Malicious" if pred == 1 else "Benign"
        confidence = float(max(prob) * 100)
        results.append({"classification": classification, "confidence": confidence})
        
    return {"results": results}
