import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
import zipfile
import xgboost as xgb
import shap

print("Extracting archive.zip...")
extract_dir = "extracted_data"
# Fail gracefully if archive.zip doesn't exist (if running multiple times)
if os.path.exists("archive.zip") and not os.path.exists(extract_dir):
    with zipfile.ZipFile("archive.zip", 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

print(f"Dataset extracted to: {extract_dir}")
csv_files = []
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.endswith('.csv'):
            csv_files.append(os.path.join(root, f))

if not csv_files:
    raise ValueError("No CSV files found in the extracted archive.")

print(f"Loading data from all {len(csv_files)} CSV files. This might take a while...")
df_list = []
for file in csv_files:
    print(f"Reading {os.path.basename(file)}...")
    df_list.append(pd.read_csv(file, skipinitialspace=True))
df = pd.concat(df_list, ignore_index=True)
print(f"Total dataset shape: {df.shape}")

df.columns = df.columns.str.strip()
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

target_col = 'Label'

def map_label(label):
    lbl = str(label).upper()
    if 'BENIGN' in lbl: return 'Safe'
    elif 'DDOS' in lbl: return 'DDoS'
    elif 'DOS' in lbl: return 'DoS'
    elif 'INFILT' in lbl or 'INFILTER' in lbl: return 'Infiltration'
    elif 'BRUTE' in lbl or 'PATATOR' in lbl or 'FTP' in lbl or 'SSH' in lbl: return 'Brute-Force'
    elif 'WEB' in lbl or 'SQL' in lbl or 'XSS' in lbl: return 'Web-Attack'
    return 'DDoS' # Fallback to DDoS

df[target_col] = df[target_col].apply(map_label)

# Filter out classes that are too rare to survive permutations
counts = df[target_col].value_counts()
valid_classes = counts[counts > 500].index
df = df[df[target_col].isin(valid_classes)]

from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df[target_col])
# Save the label mapping as a list so app.py can interpret it
joblib.dump(label_encoder.classes_.tolist(), 'classes.joblib')
X = df.drop(columns=[target_col]).select_dtypes(include=[np.number])

print("Sub-sampling for fast SHAP Feature Engineering...")
# We take a stratified subset so SHAP doesn't take 5 years to compute
if len(y) > 20000:
    X_sample, _, y_sample, _ = train_test_split(X, y, train_size=20000, random_state=42, stratify=y if len(np.unique(y)) > 1 else None)
else:
    X_sample, y_sample = X, y

print("Training Initial XGBoost for SHAP Analysis...")
xgb_initial = xgb.XGBClassifier(n_estimators=20, random_state=42, n_jobs=-1, eval_metric='mlogloss')
xgb_initial.fit(X_sample, y_sample)

print("Calculating SHAP values...")
explainer = shap.TreeExplainer(xgb_initial)
shap_values = explainer.shap_values(X_sample)

if isinstance(shap_values, list): # Multi-class SHAP outputs a list of arrays
    mean_abs_shap = np.sum([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
else:
    # If 3D, average across samples and classes to get 1D feature importance
    if len(np.shape(shap_values)) == 3:
        mean_abs_shap = np.abs(shap_values).mean(axis=0).mean(axis=1)
    else:
        mean_abs_shap = np.abs(shap_values).mean(axis=0)

top_indices = np.argsort(mean_abs_shap)[::-1][:15]
top_indices_1d = np.squeeze(top_indices) # ensure 1D
top_features = X.columns[top_indices_1d].tolist()

X_selected = X[top_features]

print("Applying SMOTE...")
if len(np.unique(y)) > 1:
    smote = SMOTE(random_state=42, k_neighbors=min(3, min(pd.Series(y).value_counts()) - 1))
    X_resampled, y_resampled = smote.fit_resample(X_selected, y)
else:
    X_resampled, y_resampled = X_selected, y

X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

print("Training final Random Forest Multi-Class model...")
rf_final = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_final.fit(X_train_scaled, y_train)

print("Training final XGBoost Multi-Class model...")
xgb_final = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, eval_metric='mlogloss')
xgb_final.fit(X_train_scaled, y_train)

print("Saving models and artifacts...")
joblib.dump(rf_final, 'rf_model.joblib')
joblib.dump(xgb_final, 'xgb_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(top_features, 'features.joblib')

print("Multi-class training complete!")
