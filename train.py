import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
import zipfile

print("Extracting archive.zip...")
extract_dir = "extracted_data"
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
    if 'BENIGN' in lbl: return 0
    return 1

y = df[target_col].apply(map_label)
X = df.drop(columns=[target_col]).select_dtypes(include=[np.number])

print("Selecting top 15 features...")
rf_initial = RandomForestClassifier(n_estimators=20, random_state=42, n_jobs=-1)
rf_initial.fit(X, y)
importances = rf_initial.feature_importances_
top_indices = np.argsort(importances)[::-1][:15]
top_features = X.columns[top_indices].tolist()

X_selected = X[top_features]

print("Applying SMOTE...")
if len(y.unique()) > 1:
    smote = SMOTE(random_state=42, k_neighbors=min(3, min(y.value_counts()) - 1))
    X_resampled, y_resampled = smote.fit_resample(X_selected, y)
else:
    X_resampled, y_resampled = X_selected, y

X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

print("Training final Random Forest model...")
rf_final = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_final.fit(X_train_scaled, y_train)

print("Saving model and artifacts...")
joblib.dump(rf_final, 'rf_model.joblib')
joblib.dump(scaler, 'scaler.joblib')
joblib.dump(top_features, 'features.joblib')

print("Training complete! Run FastAPI backend next.")
