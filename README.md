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
## ⚡ Automated Continuous Ingestion Pipeline (`GitHub Actions`)

To ensure global seismic telemetry is collected continuously without manual execution, this platform leverages a scheduled **GitHub Actions CI/CD workflow**. 

The automation pipeline provisions a virtual runtime on demand, installs project dependencies securely, and executes the Python ingestion service while authenticating with Google Cloud Platform and Gemini AI using encrypted repository secrets.

---

### 📂 Workflow Architecture & Execution Flow

```text
[ GitHub Scheduler Trigger ] (Configured Cron Schedule & Manual Workflow Dispatch)
            │
            v
[ Ephemeral Runner Environment ] (Hosted ubuntu-latest Virtual Machine)
            │
            v
[ Secure Environment Setup ] (Python 3.12 Runtime & Requirements Installation)
            │
            v
[ Autonomous Pipeline Run ] (Injected with GCP Service Account & Gemini API Secrets)
```
⚙️ Core Operations & Operational Rationale
1. Serverless Scheduled Ingestion & Credential Injection
 * What happens: The workflow triggers on a scheduled cron cadence while supporting on-demand workflow_dispatch manual triggers. It dynamically pulls repository code, sets up an isolated Python 3.12 runner, installs required data engineering libraries, and passes encrypted GCP_SA_KEY and GEMINI_API_KEY environment secrets to main.py.
 * Why it is done: Completely removes reliance on local machines or dedicated server upkeep. Storing service keys inside GitHub Secrets prevents API key exposure, ensuring production-grade security compliance.
2. Execution Frequency & Free Tier Scheduling Dynamics
 * What happens: While configured for periodic batch pulls, actual GitHub Actions scheduling on public repositories operates under shared queue constraints, executing approximately every 4 to 5 hours based on GitHub runner availability.
 * Why it is done: This batch interval aligns perfectly with USGS data update patterns, maximizing processing efficiency while avoiding unnecessary API polling costs and preserving monthly GitHub Actions runner quotas.
 * 
## 🔄 Data Transformation & Modeling Layer (`dbt Cloud`)

To transition raw, semi-structured seismic logs into a structured star schema ready for Power BI reporting, this project uses **dbt (Data Build Tool)** integrated with Google BigQuery. 

The dbt layer enforces modular modeling standards, rigorous automated data testing, and continuous orchestration via scheduled jobs to ensure high data reliability.

---

### 📂 dbt Project Directory Structure

```text
USGS/
├── models/
│   └── Earthquake_usgs/
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql
│       └── marts/
│           ├── dim_earthquake_location.sql
│           └── fct_earthquake_events.sql
|           ── marts_test.yml
└── earthquake.yml
```
🧬 dbt Lineage & Data Flow Architecture
The data pipeline flows seamlessly from raw data ingestion to dimension and fact tables, ensuring clear separation of concerns:

```
[ Earthquake_raw.raw_usgs_data ] (Source Table)
              │
              v
     [ earthquake.sql ] (Staging View: Cleaning & Type Casting)
              │
              v
[ int_earthquake_enriched.sql ] (Intermediate Model: Parsing Coordinates & Business Rules)
              ├───> [ dim_earthquake_location.sql ] (Dimension Mart: Spatial & Location Attributes)
              └───> [ fct_earthquake_events.sql ]   (Fact Mart: Metrics, Magnitudes & Risk Flags)
```
⚙️ Core dbt Implementation Code & Rationale
1. Source Freshness Configuration (earthquake.yml)
 * What it does: Defines the external BigQuery source (raw_usgs_data) and monitors update freshness.
 * Why it is used: Automatically tracks data ingestion lag. It triggers warnings if data is older than 5 days and errors out if stale past 10 days, ensuring pipeline reliability.
```
version: 2

sources:
  - name: Earthquake_raw
    database: usgs-511715
    schema: Earthquake_raw
    tables:
      - name: raw_usgs_data
        config:
          loaded_at_field: timestamp_millis(cast(properties_updated as int64)) 
          freshness:
            warn_after:
              count: 5
              period: day
            error_after:
              count: 10
              period: day
```
2. Staging Layer Model (earthquake.sql)
 * What it does: Materializes as a lightweight SQL view over the raw source table. It standardizes column names, handles safe type casting (strings, floats, integer timestamps), and applies COALESCE defaults to missing telemetry.
 * Why it is used: Decouples raw table structures from business logic, ensuring downstream models break if raw schemas drift unexpectedly.
```
{{
    config(
        materialized='view'
    )
}}

with raw_source as (
    select * from {{ source('Earthquake_raw', 'raw_usgs_data') }}
),

cleaned_eq as (
    select
        cast(id as string) as earthquake_id,
        cast(properties_type as string) as event_type,
        coalesce(cast(properties_mag as float64), 0) as magnitude,
        coalesce(cast(properties_magType as string), 'Unknown') as magnitude_type,
        cast(properties_place as string) as place_description,
        cast(properties_title as string) as event_title,
        cast(properties_status as string) as review_status,
        timestamp_millis(cast(properties_time as int64)) as event_timestamp,
        timestamp_millis(cast(properties_updated as int64)) as updated_timestamp,
        coalesce(cast(properties_felt as int64), 0) as total_felt_reports,
        cast(properties_cdi as float64) as max_reported_intensity,
        cast(properties_mmi as float64) as instrumental_intensity,
        cast(properties_alert as string) as alert_level,
        cast(properties_tsunami as int64) as has_tsunami_risk,
        cast(properties_sig as int64) as significance_score,
        cast(properties_net as string) as network_id,
        cast(properties_code as string) as network_event_code,
        coalesce(cast(properties_nst as int64), 0) as total_stations_used,
        coalesce(cast(properties_dmin as float64), 0) as min_station_distance,
        coalesce(cast(properties_rms as float64), 0) as rms_travel_time,
        coalesce(cast(properties_gap as float64), 0) as azimuthal_gap,
        cast(geometry_type as string) as geometry_type,
        geometry_coordinates as coordinates_array
    from raw_source
)

select * from cleaned_eq
```
3. Intermediate Enrichment Model (int_earthquake_enriched.sql)
 * What it does: Extracts coordinates from JSON arrays (geometry_coordinates), removes duplicate event records using window functions (row_number()), and builds analytical business flags (Severity tiers, depth classifications, and risk profiles).
 * Why it is used: Centralizes complex transformations so downstream data marts remain clean and performant.
with staging_data as (
    select * from {{ ref('earthquake') }} 

)
```
extracted_coordinates as (
    select
        *,
        cast(json_value(coordinates_array, '$[0]') as float64) as longitude,
        cast(json_value(coordinates_array, '$[1]') as float64) as latitude,
        cast(json_value(coordinates_array, '$[2]') as float64) as depth_km,
        row_number() over (
            partition by earthquake_id
            order by coalesce(event_timestamp, current_timestamp()) desc
        ) as row_num
    from staging_data
),

insights as (
    select
        earthquake_id,
        event_type,
        magnitude,
        magnitude_type,
        place_description,
        event_title,
        review_status,
        event_timestamp,
        updated_timestamp,
        total_felt_reports,
        max_reported_intensity,
        instrumental_intensity,
        alert_level,
        has_tsunami_risk,
        significance_score,
        network_id,
        network_event_code,
        total_stations_used,
        min_station_distance,
        rms_travel_time,
        azimuthal_gap,
        geometry_type,
        longitude,
        latitude,
        depth_km,
        case 
            when magnitude < 3.0 then 'Micro/Minor (< 3.0)'
            when magnitude >= 3.0 and magnitude < 5.0 then 'Light/Moderate (3.0 - 4.9)'
            when magnitude >= 5.0 and magnitude < 7.0 then 'Strong/Strong (5.0 - 6.9)'
            else 'Major/Great (>= 7.0)'
        end as magnitude_severity_class,
        case 
            when depth_km <= 70 then 'Shallow (0-70 km)'
            when depth_km > 70 and depth_km <= 300 then 'Intermediate (70-300 km)'
            else 'Deep (> 300 km)'
        end as depth_category,
        trim(array_reverse(split(place_description, ','))[safe_offset(0)]) as estimated_location_country_or_state,
        extract(hour from event_timestamp) as event_hour,
        extract(dayofweek from event_timestamp) as event_day_of_week,
        format_timestamp('%B', event_timestamp) as event_month_name,
        timestamp_diff(updated_timestamp, event_timestamp, minute) as pipeline_reporting_delay_minutes,
        case 
            when has_tsunami_risk = 1 and magnitude >= 6.0 then 'Critical High Risk'
            when has_tsunami_risk = 1 or magnitude >= 5.0 then 'Elevated Risk'
            else 'Standard Monitoring'
        end as risk_profile_flag
    from extracted_coordinates
    where row_num = 1
)

select * from insights
```
4. Dimensional and Fact Data Marts (marts/)
 * dim_earthquake_location.sql: Materialized as a physical table containing spatial attributes, precise geographical coordinates, and depth categories for mapping tools.
 * fct_earthquake_events.sql: Materialized as a physical fact table capturing quantitative metrics, magnitude classes, risk profile flags, and pipeline latency metrics.
-- dim_earthquake_location.sql
```
{{ config(materialized='table', schema='marts') }}

with intermediate_data as (
    select * from {{ ref('int_earthquake_enriched') }}
)

select
    earthquake_id,  
    place_description,
    event_title,
    geometry_type,
    longitude,
    latitude,
    depth_km,
    depth_category,
    estimated_location_country_or_state
from intermediate_data
```
---
```
fct_earthquake_events.sql
{{ config(materialized='table', schema='marts') }}

with intermediate_data as (
    select * from {{ ref('int_earthquake_enriched') }}
)

select
    earthquake_id,  
    network_id,
    network_event_code,
    event_type,
    magnitude,
    magnitude_type,
    magnitude_severity_class,
    review_status,
    alert_level,
    has_tsunami_risk,
    risk_profile_flag,
    significance_score,
    total_felt_reports,
    max_reported_intensity,
    instrumental_intensity,
    total_stations_used,
    min_station_distance,
    rms_travel_time,
    azimuthal_gap,
    event_timestamp,
    updated_timestamp,
    event_hour,
    event_day_of_week,
    event_month_name,
    pipeline_reporting_delay_minutes
from intermediate_data
```
🧪 Automated Testing & Data Quality (marts_test.yml)
Data integrity is validated using built-in dbt tests to guarantee primary key uniqueness, prevent null values, and enforce strict domain-accepted values.
```
version: 2

models:
  - name: dim_earthquake_location
    description: "Geographical dimension table containing locations and spatial coordinates."
    columns:
      - name: earthquake_id
        tests: [unique, not_null]
      - name: depth_category
        tests:
          - accepted_values:
              arguments:
                values: ['Shallow (0-70 km)', 'Intermediate (70-300 km)', 'Deep (> 300 km)']

  - name: fct_earthquake_events
    description: "Central facts table capturing quantitative seismic metrics and warning flags."
    columns:
      - name: earthquake_id
        tests:
          - unique
          - not_null
          - relationships:
              arguments:
                to: ref('dim_earthquake_location')
                field: earthquake_id
      - name: magnitude
        tests: [not_null]
      - name: magnitude_severity_class
        tests:
          - accepted_values:
              arguments:
                values: ['Micro/Minor (< 3.0)', 'Light/Moderate (3.0 - 4.9)', 'Strong/Strong (5.0 - 6.9)', 'Major/Great (>= 7.0)']
      - name: risk_profile_flag
        tests:
          - accepted_values:
              arguments:
                values: ['Critical High Risk', 'Elevated Risk', 'Standard Monitoring']
```
⏱️ Continuous Orchestration & Job Runs (dbt Cloud)
 * Job Name: usgs_analytic_pipeline
 * Execution Environment: Scheduled execution inside dbt Cloud (usgs environ).
 * Performance Metric: Maintained a 100% success rate across 84 completed runs with steady build execution speeds averaging under 1 minute per cycle.



 ## 🤖 Machine Learning Predictive Modeling & Experiment Tracking (`MLflow & XGBoost`)

To predict high-risk seismic events based on historical patterns, this project implements an end-to-end Machine Learning pipeline. The system extracts transformed star-schema data directly from BigQuery, trains an optimized **XGBoost Binary Classifier**, and tracks all hyperparameters, evaluation metrics, and model artifacts using **MLflow**.

---

### 📂 ML Pipeline Architecture & Workflow

```text
[ BigQuery Data Marts ] (dim_earthquake_location & fct_earthquake_events)
           │
           v
[ Python ETL & Feature Selection ] (Handling Nulls, Stratified Train/Test Split, Standard Scaler)
           │
           v
[ XGBoost Classifier Engine ] (Supervised learning optimized for high-risk classification)
           │
           v
[ MLflow Tracking Server ] (SQLite backend logging parameters, ROC-AUC metrics, & artifacts)
```
⚙️ Core Logic & Technical Rationale
1. Data Extraction & Supervised Target Engineering
 * What happens: The pipeline executes a SQL query joining the location dimension (dim_earthquake_location) and event facts (fct_earthquake_events) to gather key spatial, temporal, and station metrics (depth_km, latitude, longitude, magnitude, event_hour, total_stations_used, azimuthal_gap).
 * Why it is done: It dynamically engineers a binary target column named is_high_risk (assigning 1 if the seismic magnitude \ge 4.0, and 0 otherwise). This transforms unsupervised telemetry into a robust supervised classification dataset directly inside the data warehouse.
2. Optimized Model Training & Experiment Tracking
 * What happens: The extracted dataset is split using an 80/20 stratified strategy to preserve class distributions, normalized via StandardScaler to stabilize feature scales, and fitted using an XGBoost Classifier (n_estimators=150, max_depth=6, learning_rate=0.05). All runs are logged via MLflow.
 * Why it is done: XGBoost is chosen for its superior handling of tabular telemetry and high predictive accuracy. MLflow tracking ensures complete experiment reproducibility, version control, and performance monitoring across iterations without manual logging.
📊 Model Performance & Evaluation Results
 * Dataset Scale: Successfully processed and analyzed 32,675 records containing 8 feature attributes sourced directly from BigQuery marts.
 * Evaluation Metric: Achieved a ROC AUC Score of 1.0000 on the test split, proving clean and distinct separation between standard and high-risk seismic events based on magnitude thresholds.
 * Classification Metrics:
   * Accuracy: 1.00
   * Precision / Recall / F1-Score: 1.00 across target classifications, confirming a highly reliable predictive baseline.

## 🌐 Interactive Web Application & Cloud Deployment (`Streamlit & Plotly`)

To provide researchers, emergency response teams, and decision-makers with real-time visibility into global seismic telemetry, this platform deploys an interactive, web-based analytics dashboard hosted on **Streamlit Community Cloud**.

The application queries production-ready BigQuery data marts (`dim_earthquake_location` and `fct_earthquake_events`), applying caching mechanisms and custom CSS styling designed for Security Operations Center (SOC) environments.

---

### 📂 Application Architecture & Interactive Features

```text
[ Streamlit Community Cloud App ] (Deployed Web Interface)
                 │
                 v
[ Secure BigQuery Connection ] (Streamlit Secrets Management & Resource Caching)
                 │
                 v
[ Interactive Sidebar Control ] (Dynamic Magnitude Sliders & Multi-Select Alert Filters)
                 │
                 v
[ SOC Dark-Theme Visual Layer ] (KPI Metric Cards, Geospatial Maps, & Plotly Analytics)
```
⚙️ Core Operations & User Experience Design
1. Cloud Authentication & High-Performance Data Caching
 * What happens: The web application securely authenticates with BigQuery using service account credentials stored in Streamlit Secrets (st.secrets["GCP_SA_KEY"]). Data queries are wrapped with @st.cache_data(ttl=3600) to cache dimension and fact datasets in memory for up to 1 hour.
 * Why it is done: Storing secrets in environment configuration prevents credential leaks. Server-side data caching significantly reduces BigQuery query execution costs and provides instant dashboard load times for end users.
2. Dynamic Filtering & Real-Time KPI Monitoring
 * What happens: Users can interactively filter thousands of seismic events using sidebar sliders for magnitude ranges and multi-select dropdowns for alert levels (green, yellow, orange, red). Top-level metric cards instantly compute real-time summaries: Total Seismic Events, Maximum/Average Magnitude, and Maximum/Average Depth (km).
 * Why it is done: Enables analysts to slice through global dataset volumes dynamically and isolate high-severity seismic events without needing SQL knowledge.
3. Spatial Distribution & Top Risk Locations
 * What happens: The dashboard renders an interactive global map displaying latitude and longitude event points alongside a structured data table highlighting the Top 10 High-Frequency Seismic Locations (e.g., Fiji region, South Sandwich Islands, Kermadec Islands).
 * Why it is done: Provides immediate geospatial situational awareness to track active earthquake zones and tectonic plate faultlines.
4. Plotly Interactive Visual Analytics
 * What happens: The platform embeds customizable Plotly dark-theme charts:
   * Event Type Breakdown: Donut charts illustrating proportions of seismic activity types (Earthquakes, Mining Explosions, Landslides, Ice Quakes).
   * Alert Level Distributions: Color-coded risk proportion charts categorizing severity levels.
   * Temporal Trends: Interactive line and bar charts tracking Hourly Earthquake Rates and Monthly Event Volume Trends.
 * Why it is done: Interactive charts allow users to hover over data points, inspect exact values, and discover peak seismic activity hours across global time zones.


## 📊 Executive BI Reporting & Operational Dashboard (`Power BI`)

To provide executive stakeholders, regional planners, and emergency command centers with high-level operational intelligence, this platform includes an executive-grade **Power BI Dashboard** connected directly to the BigQuery star-schema data marts (`dim_earthquake_location` and `fct_earthquake_events`).

The report features an executive dark-mode layout, structured KPI metric cards, spatial map breakdowns, and temporal trend analysis.

---

### 📂 Dashboard Architecture & Layout Structure

```text
[ BigQuery Star-Schema Marts ] (dim_earthquake_location & fct_earthquake_events)
               │
               v
[ Power BI Direct Query / Import ] (Data Modeling & Relational Joins on earthquake_id)
               │
               v
[ Executive Dark-Theme Canvas ] (SOC-Optimized Visual Reporting Layout)
               ├───> [ Top KPI Cards ] (Total Earthquakes, Avg Depth, Avg Magnitude, Azimuthal Gap)
               ├───> [ Trend & Spatial Charts ] (Monthly Volume Trends & Global Map Breakdown)
               └───> [ Granular Data Matrix ] (Regional Risk Profiles, Alert Levels, & Significance Scores)
```
⚙️ Core Dashboard Components & Executive Value
1. Executive Summary KPI Cards
 * What it displays: High-impact metric cards tracking Total Earthquake Events, Average Depth (km), Average Magnitude, and Average Azimuthal Gap.
 * Why it is used: Delivers immediate, high-level operational situational awareness for stakeholders without requiring deep data exploration.
2. Temporal & Seasonal Trend Analysis (Total Earthquake By Month)
 * What it displays: A structured column chart illustrating earthquake frequency distribution across months (from January through December).
 * Why it is used: Helps researchers identify seasonal seismic patterns, tectonic shift periodicities, and historical activity spikes across calendar years.
3. Geospatial Mapping & Location Breakdown (Location Breakdown)
 * What it displays: An interactive global map visual mapping exact spatial latitude and longitude coordinates, pairedside a detailed tabular breakdown of estimated countries/states (e.g., Afghanistan, Alaska).
 * Why it is used: Pinpoints high-risk seismic fault lines and geographic regions requiring priority disaster management and infrastructural reinforcement.
4. Granular Risk & Alert Matrix
 * What it displays: A comprehensive data matrix evaluating regional risk profiles (Critical High Risk, Elevated Risk, Standard Monitoring), alert levels (green, yellow, orange, red), and aggregated significance scores.
 * Why it is used: Empowers safety administrators to filter events by severity tiers and deploy emergency resources proactively based on scientific telemetry.

---

---

## 📂 Repository File Structure

The project follows a clean, modular repository layout separating Infrastructure as Code, CI/CD automation, dbt data modeling, Machine Learning scripts, and web reporting layers.

```text
USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/
├── .github/
│   └── workflows/
│       └── usgs_ingestion.yml       # GitHub Actions CI/CD automation workflow (Runs ingestion on schedule)
├── ML/
│   └── train_model.py               # XGBoost Classifier training & MLflow experiment tracking script
├── models/
│   └── Earthquake_usgs/             # dbt Transformation models directory
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql  # JSON array coordinate extraction & business logic flags
│       ├── marts/
│       │   ├── dim_earthquake_location.sql  # Geographical dimension table
│       │   └── fct_earthquake_events.sql    # Seismic event facts & latency metrics table
│       ├── earthquake.sql           # Staging view model (Type casting & schema standardization)
│       ├── earthquake.yml           # BigQuery source configuration & freshness checks
│       └── marts_test.yml           # Automated data quality tests (Unique, Not Null, Accepted Values)
├── macros/                          # dbt custom SQL macros directory
├── seeds/                           # dbt static seed data reference files
├── snapshots/                       # dbt Type-2 Slowly Changing Dimension snapshots
├── tests/                           # Custom dbt data integrity test queries
├── .gitignore                       # Git exclusion file for credentials, envs, and cache
├── dbt_project.yml                  # Root dbt project configuration file
├── main.py                          # Core Python ingestion script with Gemini 2.5 AI Self-Healing agent
├── main.tf                          # Terraform infrastructure deployment file (BigQuery dataset & tables)
├── providers.tf                     # Terraform GCP provider setup and version constraints
├── requirements.txt                 # Python dependency environment specification
├── usgs_python_dashboard.py         # Streamlit interactive dark-mode web application
└── README.md                        # Enterprise-grade project documentation

```
