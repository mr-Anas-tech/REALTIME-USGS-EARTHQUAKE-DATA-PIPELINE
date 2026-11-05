import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import mlflow
import xgboost as xgb
import mlflow.xgboost
from google.cloud import bigquery

# Google Colab Credentials Setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usgs-511715-2f007f20ac30.json"

# SQLite Tracking URI Setup for Colab
mlflow.set_tracking_uri("sqlite:///mlflow.db")
experiment_name = "USGS_earthquake_risk_prediction_colab"

experiment = mlflow.get_experiment_by_name(experiment_name)
if experiment is None:
    mlflow.create_experiment(name=experiment_name)

mlflow.set_experiment(experiment_name)

# BigQuery Client Initialization
client = bigquery.Client()
print("Gcp service account credentials loaded successfully.")

query = """
    select
         loc.depth_km,
          loc.latitude,
          loc.longitude,
          fct.magnitude,
          fct.event_hour,
          fct.total_stations_used,
          fct.azimuthal_gap,
          IF(fct.magnitude >= 4.0, 1, 0) as is_high_risk
    FROM `usgs-511715.raw_usgs_data_marts.dim_earthquake_location` as loc
    join `usgs-511715.raw_usgs_data_marts.fct_earthquake_events` as fct
          ON fct.earthquake_id = loc.earthquake_id
    WHERE fct.magnitude IS NOT NULL
"""

print("Executing query to fetch data from BigQuery...")
df = client.query(query).to_dataframe()
print("Data shape loaded:", df.shape)

X = df[['depth_km', 'latitude', 'longitude', 'magnitude', 'event_hour', 'total_stations_used', 'azimuthal_gap']].fillna(0)
y = df['is_high_risk']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# MLflow Training & Logging Execution (Cleaned for Colab)
with mlflow.start_run():
    params = {
        "n_estimators": 150,
        "max_depth": 6,
        "learning_rate": 0.05,
        "random_state": 42
    }

    model = xgb.XGBClassifier(**params)
    model.fit(X_train_scaled, y_train)

    # Evaluate the model
    preds = model.predict(X_test_scaled)
    probs = model.predict_proba(X_test_scaled)[:, 1]
    auc_score = roc_auc_score(y_test, probs)

    # Log metrics and parameters to MLflow DB
    mlflow.log_params(params)
    mlflow.log_metric("roc_auc", auc_score)
    mlflow.xgboost.log_model(model, artifact_path="xgboost_earthquake_model")

    print(f"\n--- Model training completed successfully on Colab! ---")
    print(f"ROC AUC Score: {auc_score:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, preds))
    
