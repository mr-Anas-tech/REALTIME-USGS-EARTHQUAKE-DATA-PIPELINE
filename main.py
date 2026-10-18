from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import requests


def run_usgs_pipeline():
    # Dynamic 1-year date range calculation
    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d')

    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}'
    print(f"Generated URL: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print (f"Error fetching data from USGS API: {response.status_code}")
        return

    data = response.json()
    features = data.get("features", [])
    print(f"Fetched {len(features)} earthquake records from USGS API.")

    if not features:
        print("No earthquake data found in the last hour.")
        return

    df = pd.json_normalize(features)
    df.columns = df.columns.str.replace('.', '_', regex=False)

    project_id = "usgs-511715"
    dataset_id = "Earthquake_raw"
    table_id = "raw_usgs_data"
    full_tabble_path = f"{project_id}.{dataset_id}.{table_id}"

    if "GCP_SA_KEY" not in os.environ:
        raise ValueError("GCP_SA_KEY environment variable not set. Please set it to your GCP service account key.")

    service_account_info = json.loads(os.environ["GCP_SA_KEY"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    bq_client = bigquery.Client(credentials=credentials, project=project_id)


    try:
        query = f"SELECT * FROM `{full_tabble_path}`"
        existing_ids = set(row['id'] for row in bq_client.query(query).result())
        print(f"Found {len(existing_ids)} existing earthquake records in BigQuery.")
    except Exception as e:
        print( f"table minght not exist yet, creating new table. Error: {e}")
        existing_ids = set()

    if "id" in df.columns and existing_ids:
        df = df[~df["id"].isin(existing_ids)]
    if df.empty:
        print("All earthquake records from the last hour already exist in BigQuery. No new records to insert.")
        return

    print(f"Inserting {len(df)} new earthquake records into BigQuery.")

    df.to_gbq(
        destination_table=full_tabble_path,
        project_id=project_id,
        credentials=credentials,
        if_exists="append",
        progress_bar=False
    )

    print(f"Successfully appended {len(df)} new earthquake records to BigQuery table {full_tabble_path}.")

if __name__ == "__main__":
    run_usgs_pipeline()

