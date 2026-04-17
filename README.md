Project Overview
This repository implements a Streamlit dashboard, a FastAPI inference endpoint, and training utilities for a Random Forest‑based intrusion detection system (IDS). The README and EXPLANATION files describe the behavioral-AI approach, SMOTE balancing, and Random Forest voting logic used by the project.

Repository structure
This section lists the main files and their purpose in the repository.

app.py — Streamlit dashboard UI and client-side inference flow.
api.py — FastAPI backend providing the /analyze-traffic endpoint for model inference.
train.py — Data extraction, feature selection, SMOTE resampling, model training, and artifact saving.
requirements.txt — Python package dependencies.
README.md / EXPLANATION.md — Project description and pipeline overview.
Streamlit dashboard (app.py)
The Streamlit app loads model artifacts, accepts CSV uploads, sanitizes data, runs inference locally (or via backend), and presents a threat intelligence report with visualizations and CSV export. Key behaviors include:

Loading rf_model.joblib, scaler.joblib, and features.joblib at startup.
CSV upload and preprocessing: trim columns, replace infinite values, fill NaNs.
Running model inference, computing classification and confidence per flow, and storing results in session state.
Displaying summary metrics, pie chart, high-confidence alerts, and download button for report CSV.
Example: model loading call in app.py

# app.py (snippet)
import joblib
model = joblib.load('rf_model.joblib')
scaler = joblib.load('scaler.joblib')
features = joblib.load('features.joblib')
FastAPI backend (api.py)
The FastAPI app exposes a POST /analyze-traffic endpoint that:

Expects a JSON payload with an array of records under the "data" field.
Loads model artifacts (rf_model.joblib, scaler.joblib, features.joblib) and returns HTTP 500 if not loaded.
Validates presence of required feature columns and returns 400 when missing.
Processes numeric features, scales them, predicts classes and probabilities, and returns classification and confidence for each record.
API: Analyze Traffic
POST /analyze-traffic
Analyze Traffic
Export to Postman
Classify uploaded network flow records as Malicious or Benign and return confidence per record.

POST
http://localhost:8000/analyze-traffic
Headers
Content-Type
string • header
required
application/json

Request body
JSON payload required for this request.

{
  "data": [
    {"feature1": 0.1, "feature2": 3.4, ...},
    {"feature1": 0.2, "feature2": 1.2, ...}
  ]
}
Code examples
curl -X POST "http://localhost:8000/analyze-traffic" \
  -H "Content-Type: application/json" \
  -H "Content-Type: application/json" \
  -d '{
  \"data\": [
    {\"feature1\": 0.1, \"feature2\": 3.4, ...},
    {\"feature1\": 0.2, \"feature2\": 1.2, ...}
  ]
}'
Responses
200
400
500
Success

{
  "results": [
    {"classification": "Benign", "confidence": 86.5},
    {"classification": "Malicious", "confidence": 92.1}
  ]
}
Missing feature columns

{
  "detail": "Missing columns: ['colA', 'colB']"
}
Model artifacts not loaded

{
  "detail": "Model not loaded."
}
Reference: endpoint implementation and payload model in api.py.

Training pipeline (train.py)
The training script performs the following steps:

Extracts CSV files from archive.zip into an extracted_data directory.
Reads and concatenates CSVs, trims columns, removes NaNs and infinities, and maps the Label column to binary targets.
Selects numeric columns and uses a preliminary RandomForest (n_estimators=20) to compute feature importances; selects top 15 features.
Applies SMOTE to balance classes (k_neighbors chosen relative to minority class counts).
Splits data, standardizes features with StandardScaler, and trains a final RandomForest with n_estimators=100.
Saves rf_model.joblib, scaler.joblib, and features.joblib for use by the dashboard and API.
Example training artifact saves:

joblib.dump(rf_final, 'rf_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(top_features, 'features.joblib')
Dependencies
The project lists required packages in requirements.txt. Key packages include Streamlit, scikit-learn, pandas, numpy, joblib, imbalanced-learn, plotly, and pydantic.

requirements.txt (rendered)

streamlit
scikit-learn
pandas
numpy
joblib
imbalanced-learn
plotly
pydantic
Usage summary
Train model: run train.py after placing dataset archive.zip in repo root. Artifacts saved: rf_model.joblib, scaler.joblib, features.joblib.
Start API: run the FastAPI app (e.g., uvicorn api:app --reload) to serve /analyze-traffic.
Start UI: run Streamlit (e.g., streamlit run app.py) to open the dashboard for CSV uploads and analysis. The UI loads the saved artifacts and runs inference.
Key implementation details and behaviors
Label mapping: Labels containing 'BENIGN' are mapped to 0; all others map to 1 for malicious.
Feature selection: Top 15 numeric features chosen by initial RandomForest importance.
Inference output: Each record is returned with "classification" ("Malicious" or "Benign") and "confidence" (percentage). This format is used both in UI session state and API responses.
Files cited
README.md / EXPLANATION.md — project overview and pipeline description.
app.py — Streamlit application and client inference logic.
api.py — FastAPI inference endpoint implementation.
train.py — training flow, SMOTE usage, feature selection, and artifact saving.
requirements.txt — dependency list.
