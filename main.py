import os
import json
import requests
import pandas as pd
import pandas_gbq  # Modern replacement for df.to_gbq to avoid deprecation warnings
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
from google import genai  # Google GenAI SDK for Gemini models

# ---------------------------------------------------------
# AI Self-Healing Agent Function (Powered by Gemini)
# ---------------------------------------------------------
def ai_self_heal_data(df: pd.DataFrame, error_message: str) -> pd.DataFrame:
    """
    Analyzes schema or data conversion errors using Gemini 
    and automatically fixes or cleans the Pandas DataFrame.
    """
    print(f"\n🤖 [AI SELF-HEALER TRIGGERED] Analyzing Error with Gemini...")
    
    # Initialize Google GenAI client using GEMINI_API_KEY environment variable
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    sample_data = df.head(2).to_dict(orient="records")
    columns_list = list(df.columns)
    
    prompt = f"""
    You are an expert Data Pipeline Self-Healing Agent.
    A Python Pandas DataFrame failed during insertion into BigQuery.

    ERROR TRACEBACK:
    {error_message}

    DATAFRAME COLUMNS:
    {columns_list}

    SAMPLE ROWS (JSON):
    {json.dumps(sample_data, default=str)}

    INSTRUCTIONS:
    Identify which columns caused the failure (e.g., nested lists, bad data types, unhandled nulls, incompatible string formats).
    Return a JSON object with instructions on column fixes in this EXACT structure:
    {{
      "columns_to_stringify": ["col1", "col2"],
      "columns_to_drop": ["col3"]
    }}
    ONLY output valid JSON. No prose or markdown headers.
    """

    try:
        # Generate content using Gemini model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        raw_json = response.text.strip()
        # Clean response if wrapped in markdown code blocks
        if raw_json.startswith("```json"):
            raw_json = raw_json.split("```json")[1].split("```")[0].strip()
        elif raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1].split("```")[0].strip()
            
        fix_instructions = json.loads(raw_json)
        print(f"🤖 [AI SELF-HEALER DECISION]: {fix_instructions}")
        
        # Apply AI's recommended fixes dynamically
        for col in fix_instructions.get("columns_to_stringify", []):
            if col in df.columns:
                df[col] = df[col].astype(str)
                
        for col in fix_instructions.get("columns_to_drop", []):
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
                
        print("✅ [AI SELF-HEALER] DataFrame successfully healed!")
        return df

    except Exception as ai_err:
        print(f"❌ [AI SELF-HEALER FAILED]: Could not fix automatically. Details: {ai_err}")
        raise

# ---------------------------------------------------------
# Main Pipeline Function
# ---------------------------------------------------------
def run_usgs_pipeline():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1) 
    
    start_str = start_time.strftime('%Y-%m-%d')
    end_str = end_time.strftime('%Y-%m-%d')
    
    # Clean USGS API URL construction
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_str}&endtime={end_str}&minmagnitude=0.05'
    print(f"Fetching earthquake data from {start_str} to {end_str}")
    
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
        print(f"Fetched {len(features)} records.")
    else:
        print(f"Error fetching data: {response.status_code}")
        return

    if not features:
        print("No earthquake data found.")
        return

    df = pd.json_normalize(features)
    df.columns = df.columns.str.replace('.', '_', regex=False)
    
    # Standard cleaning for nested list types
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else None)

    project_id = "usgs-511715"
    dataset_id = "Earthquake_raw"
    table_id = "raw_usgs_data"
    full_tabble_path = f"{project_id}.{dataset_id}.{table_id}"

    if "GCP_SA_KEY" not in os.environ:
        raise ValueError("GCP_SA_KEY environment variable not set.")

    service_account_info = json.loads(os.environ["GCP_SA_KEY"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    bq_client = bigquery.Client(credentials=credentials, project=project_id)

    # FIXED: Using properties_time instead of time to prevent BigQuery query error
    try:
        query = f"SELECT id FROM `{full_tabble_path}` WHERE properties_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)"
        existing_ids = set(row['id'] for row in bq_client.query(query).result())
    except Exception as e:
        print(f"Table query warning: {e}")
        existing_ids = set()

    if "id" in df.columns and existing_ids:
        df = df[~df["id"].isin(existing_ids)]

    if df.empty:
        print("No new records to insert.")
        return

    print(f"Attempting to insert {len(df)} records into BigQuery...")

    # ---------------------------------------------------------
    # Execution with Gemini AI Self-Healing Attempt
    # ---------------------------------------------------------
    try:
        # First Attempt: Normal BigQuery insertion using pandas_gbq
        pandas_gbq.to_gbq(
            dataframe=df,
            destination_table=full_tabble_path,
            project_id=project_id,
            credentials=credentials,
            if_exists="append",
            progress_bar=False
        )
        print("Successfully written to BigQuery on first attempt!")

    except Exception as bq_err:
        print(f"⚠️ Initial BigQuery Write Failed: {bq_err}")
        
        # Self-Healing Trigger: If schema/data type error occurs, check for Gemini API key
        if "GEMINI_API_KEY" in os.environ:
            # Apply Gemini AI fixes
            healed_df = ai_self_heal_data(df, str(bq_err))
            
            print("Re-attempting BigQuery write with AI-healed dataset...")
            pandas_gbq.to_gbq(
                dataframe=healed_df,
                destination_table=full_tabble_path,
                project_id=project_id,
                credentials=credentials,
                if_exists="append",
                progress_bar=False
            )
            print("🎉 SUCCESS: Gemini AI Self-Healing resolved the issue and pipeline completed!")
        else:
            print("GEMINI_API_KEY environment variable missing. Cannot trigger AI Self-Healing.")
            raise bq_err

if __name__ == "__main__":
    run_usgs_pipeline()
