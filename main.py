from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 1. Self-Healing Decorator: API & BigQuery Connection Failures ko Handle karne ke liye
@retry(
    stop=stop_after_attempt(3), # 3 dafa try karega
    wait=wait_exponential(multiplier=1, min=2, max=10), # Exponential backoff (2s, 4s, 8s)
    reraise=True
)
def fetch_usgs_data_with_retry(url):
    print(f"Executing USGS API Fetch...")
    response = requests.get(url, timeout=15) # Timeout set kiya taake script hang na ho
    response.raise_for_status() # 4xx ya 5xx status code par retry trigger karega
    return response.json()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def execute_bq_query_with_retry(bq_client, query):
    return set(row['id'] for row in bq_client.query(query).result())


def run_usgs_pipeline():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1) 
    
    start_str = start_time.strftime('%Y-%m-%d')
    end_str = end_time.strftime('%Y-%m-%d')
    
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_str}&endtime={end_str}&minmagnitude=0.05'
    print(f"Fetching earthquake data from {start_str} to {end_str}")
    
    # Self-healing API fetch
    try:
        data = fetch_usgs_data_with_retry(url)
        features = data.get("features", [])
        print(f"Fetched {len(features)} records successfully.")
    except Exception as e:
        print(f"[SELF-HEALING FAILED] Unable to fetch data from USGS API after 3 retries. Error: {e}")
        return

    if not features:
        print("No earthquake data found.")
        return

    # Data Transformation & Cleaning
    df = pd.json_normalize(features)
    df.columns = df.columns.str.replace('.', '_', regex=False)
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else None)
        elif df[col].dtype == 'object':
            df[col] = df[col].astype(str).replace({'None': None, 'nan': None, '<NA>': None})
    
    project_id = "usgs-511715"
    dataset_id = "Earthquake_raw"
    table_id = "raw_usgs_data"
    full_tabble_path = f"{project_id}.{dataset_id}.{table_id}"

    if "GCP_SA_KEY" not in os.environ:
        raise ValueError("GCP_SA_KEY environment variable not set.")

    service_account_info = json.loads(os.environ["GCP_SA_KEY"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    bq_client = bigquery.Client(credentials=credentials, project=project_id)

    # 2. Cost & Performance Self-Healing Optimization (Full Table Scan se bachna)
    # Poori table SELECT * karne ke bajaye sirf recent 2 days ki IDs mangwa rahe hain
    try:
        query = f"SELECT id FROM `{full_tabble_path}` WHERE time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)"
        existing_ids = execute_bq_query_with_retry(bq_client, query)
        print(f"Found {len(existing_ids)} recent earthquake records in BigQuery.")
    except Exception as e:
        print(f"Table might not exist yet or query failed. Creating/appending fresh dataset. Details: {e}")
        existing_ids = set()

    # Deduplication
    if "id" in df.columns and existing_ids:
        df = df[~df["id"].isin(existing_ids)]

    if df.empty:
        print("All fetched records already exist in BigQuery. No new records to insert.")
        return

    print(f"Inserting {len(df)} new earthquake records into BigQuery.")

    # 3. BigQuery Write Self-Healing Wrapper
    try:
        df.to_gbq(
            destination_table=full_tabble_path,
            project_id=project_id,
            credentials=credentials,
            if_exists="append",
            progress_bar=False
        )
        print(f"Successfully appended {len(df)} new earthquake records to BigQuery table {full_tabble_path}.")
    except Exception as e:
        print(f"[WRITE ERROR] BigQuery Write failed: {e}")

if __name__ == "__main__":
    run_usgs_pipeline()

