# USGS Global Seismic Activity Tracker & Self-Healing Pipeline 🌍

A modern, cloud-native Analytics Engineering platform engineered to extract, transform, and analyze global earthquake telemetry provided by the United States Geological Survey (USGS).

This platform moves beyond basic data extraction by introducing an **AI-powered Self-Healing Pipeline Architecture**. By pairing Google BigQuery and Terraform with Gemini 2.5 Flash, the system detects runtime schema drifts and type mismatch failures during ingestion, auto-remediates bad records in-memory, and resumes execution without pipeline downtime.

---

## 🛠️ Tech Stack & Tooling Rationale

| Tool / Technology | Role in Architecture | Technical Rationale & Business Purpose |
| :--- | :--- | :--- |
| **HCP Terraform Cloud** | Infrastructure as Code (IaC) | Declaratively provisions and manages cloud assets (BigQuery raw datasets and target tables). Eliminates manual setup, prevents configuration drift, and ensures reproducible deployment environments across teams. |
| **Google Cloud Platform (BigQuery)** | Data Warehouse | Serves as the central serverless repository. Raw GeoJSON telemetry is ingested directly into `Earthquake_raw.raw_usgs_data` to support decoupled processing, high-throughput queries, and downstream transformation layers. |
| **Python 3.12+ (Pandas & `pandas-gbq`)** | Data Orchestration & ETL | Handles REST API polling, JSON normalization, duplicate checking, and bulk streaming writes into BigQuery. Utilizes modern `pandas-gbq` drivers to maintain memory-efficient data loading. |
| **Google GenAI SDK (`gemini-2.5-flash`)** | AI Self-Healing Agent | Acts as an automated fallback layer during ingestion failures. It inspects live error tracebacks and payload samples to repair schema mismatches (e.g., stringifying nested arrays or dropping conflicting columns) on the fly. |
```
---

## 📐 System Architecture & Data Flow


+----------------------------------+
|         USGS Public API          |
|   (Real-Time GeoJSON Telemetry)   |
+----------------+-----------------+
|
v
+----------------------------------+
|       Python Ingestion Engine    |
|  - JSON Normalization            |
|  - Dynamic Column Cleaning       |
|  - Deduplication via BQ Query    |
+----------------+-----------------+
|
[ Attempt BigQuery Ingestion ]
|
+-----------------+-----------------+
|                                   |
(Write Successful)                   (Write Failed / Schema Error)
|                                   |
v                                   v
+------------------------------+   +-------------------------------+
| GCP BigQuery Raw Dataset     |   |  Gemini AI Self-Healing Agent |
| (Earthquake_raw.raw_usgs_data)|   |  - Error Traceback Inspection |
+------------------------------+   |  - Dynamic DataFrame Repair   |
+---------------+---------------+
|
[ Re-Attempt Write ]
|
v
+-------------------------------+
| GCP BigQuery Raw Dataset      |
+-------------------------------+

---
```
## ⚙️ Core Technical Implementation

### 1. Declarative Infrastructure Provisioning (`Terraform`)

Cloud resources are fully managed via Terraform modules to guarantee immutable deployments:

* **Dataset Definition (`main.tf`):** Defines the `Earthquake_raw` dataset with explicitly set retention policies in the `US` multi-region location.
* **Table Definition (`main.tf`):** Provisions `raw_usgs_data` with deletion protection disabled for development agility, relying on dynamic schema discovery upon initial load.
* **Provider Configuration (`providers.tf`):** Binds execution to the target GCP project (`usgs-511715`) using modern HashiCorp Google provider constraints (`~>5.0`).

```hcl
# Infrastructure snippet from main.tf
resource "google_bigquery_dataset" "Earthquake_raw" {
  dataset_id                 = "Earthquake_raw"
  friendly_name              = "Earthquake Raw Data"
  description                = "Dataset for storing USGS earthquake raw data"
  location                   = "US"
  delete_contents_on_destroy = false
}

resource "google_bigquery_table" "raw_usgs_data" {
  dataset_id          = google_bigquery_dataset.Earthquake_raw.dataset_id
  table_id            = "raw_usgs_data"
  deletion_protection = false
}
```
2. Autonomous Ingestion & Deduplication (main.py)
The ingestion service performs delta updates to avoid writing duplicate records into BigQuery:
 * Time-Window Filtering: Fetches a rolling 24-hour window of event data using starttime and endtime parameters targeting seismic magnitude levels \ge 0.05.
 * State Verification Query: Queries existing event records from BigQuery across the last 2 days using TIMESTAMP_MILLIS(CAST(properties_time AS INT64)) to prevent duplicate primary key (id) inserts.
 * Complex Object Handling: Scans normalized DataFrame columns for nested list structures and converts them to JSON strings prior to loading.
3. AI-Powered Pipeline Self-Healing (Gemini Agent)
Traditional ETL pipelines fail when source API schemas change unexpectedly or data types drift. To guarantee zero-downtime operations, this engine integrates an AI Self-Healing Agent:
 * Failure Interception: If pandas_gbq.to_gbq() raises a schema or data type exception, execution is caught inside a fallback try-except block.
 * Context Delivery to Gemini: The agent sends the exact error traceback, current column names, and sample JSON rows to gemini-2.5-flash.
 * Structured Remediation Decisions: Gemini returns a strictly validated JSON instruction payload detailing repair steps (e.g., stringifying unhandled arrays or removing illegal attributes).
 * In-Memory Healing & Retry: The Pandas DataFrame is transformed dynamically according to Gemini’s instructions and re-submitted to BigQuery without human intervention.
# Self-healing execution flow
```try:
    pandas_gbq.to_gbq(df, destination_table=full_tabble_path, ...)
except Exception as bq_err:
    if "GEMINI_API_KEY" in os.environ:
        healed_df = ai_self_heal_data(df, str(bq_err))
        pandas_gbq.to_gbq(healed_df, destination_table=full_tabble_path, ...)
```
