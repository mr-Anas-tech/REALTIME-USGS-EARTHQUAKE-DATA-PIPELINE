🌍 USGS Global Seismic Activity Tracker & AI Self-Healing Pipeline

https://github.com/USERNAME/USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/actions/workflows/usgs_ingestion.yml/badge.svg
https://img.shields.io/badge/dbt-Cloud-FF694B?logo=dbt&logoColor=white
https://img.shields.io/badge/BigQuery-Google_Cloud-4285F4?logo=google-cloud&logoColor=white
https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white
https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white
https://img.shields.io/badge/Power_BI-Dashboard-F2C811?logo=powerbi&logoColor=black
https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white
https://img.shields.io/badge/License-MIT-yellow.svg

An enterprise-grade, cloud-native Analytics Engineering platform that ingests, transforms, models, and predicts global earthquake telemetry from the United States Geological Survey (USGS) — powered by an AI self-healing ingestion engine that eliminates pipeline downtime.

---

📖 Executive Summary

Traditional ETL pipelines are brittle. A single upstream schema change or unexpected data-type drift can halt critical ingestion — silently breaking dashboards, ML models, and downstream reporting for hours.

This platform was engineered to solve that problem. It ingests real-time global seismic telemetry from the USGS public API and pairs Google BigQuery + Terraform + dbt Cloud with an AI-powered self-healing agent (Gemini 2.5 Flash) that detects schema drift and type-mismatch failures mid-execution, auto-remediates malformed records in memory, and resumes writes to BigQuery — without human intervention.

The result is a zero-downtime, fully observable, end-to-end analytics platform spanning ingestion → transformation → ML prediction → executive BI.

---

🎯 Key Capabilities

Capability Description
🔄 Autonomous Ingestion Scheduled GitHub Actions runs every ~4–5 hours, polling a rolling 24-hour USGS window with deduplication against BigQuery state.
🩺 AI Self-Healing Gemini 2.5 Flash receives live error tracebacks, inspects payloads, and returns validated JSON repair instructions — executed in-memory before retry.
🏗 Immutable Infrastructure Terraform provisions BigQuery datasets and tables declaratively — no manual console clicks, no configuration drift.
🧬 Modular dbt Modeling Staging → Intermediate → Dimension/Fact star schema with source freshness monitoring and automated data-quality tests.
🤖 ML Prediction XGBoost binary classifier for high-risk event detection, experiment-tracked end-to-end via MLflow.
🌐 Interactive Dashboard Streamlit SOC-style dark web app with real-time filters, KPI cards, geospatial map, and Plotly analytics.
📊 Executive BI Power BI dark-mode command-center dashboard for stakeholders, emergency response, and regional planners.

---

🛠️ Tech Stack & Engineering Rationale

Layer Technology Why It Was Chosen
Infrastructure HCP Terraform Cloud Declarative, reproducible cloud provisioning. Eliminates manual setup and ensures identical environments across teams.
Data Warehouse Google BigQuery Serverless, columnar, sub-second queries at petabyte scale. Zero infrastructure management for high-throughput ingestion.
Ingestion Engine Python 3.12 + Pandas + pandas-gbq Mature REST/JSON handling, memory-efficient bulk streaming into BigQuery via modern drivers.
AI Remediation Google GenAI SDK (gemini-2.5-flash) Automated fallback agent — inspects error tracebacks and payload samples, returns structured repair instructions with low latency.
Orchestration (CI/CD) GitHub Actions Serverless scheduling, encrypted secret management, zero-cost runners for public repos.
Transformation dbt Cloud Modular SQL modeling, built-in tests, source freshness, and scheduled job orchestration with full lineage.
ML Training XGBoost + MLflow Best-in-class tabular performance + reproducible experiment tracking with artifact versioning.
Web App Streamlit + Plotly Rapid deployment of interactive, cache-backed analytics with SOC-grade dark theming.
BI Reporting Power BI Executive-ready visuals with native BigQuery connectivity and row-level security.

---

📐 System Architecture

```text
┌──────────────────────────────────┐
│       USGS Public REST API       │
│  (Real-Time GeoJSON Telemetry)   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│    Python Ingestion Engine       │
│  • JSON Normalization            │
│  • Dynamic Column Cleaning       │
│  • Deduplication via BQ Query    │
└──────────────┬───────────────────┘
               │
       [ Attempt BigQuery Write ]
               │
      ┌────────┴────────┐
      │                 │
 (Success)         (Schema Error)
      │                 │
      ▼                 ▼
┌──────────────┐  ┌────────────────────────────┐
│  BigQuery    │  │  Gemini 2.5 Flash Agent    │
│  Raw Dataset │  │  • Traceback Inspection    │
│  (raw_usgs)  │  │  • Dynamic DataFrame Repair│
└──────────────┘  └────────────┬───────────────┘
                               │
                       [ Re-Attempt Write ]
                               │
                               ▼
                    ┌──────────────────────┐
                    │  BigQuery Raw Dataset│
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   dbt Cloud Models   │
                    │  Staging → Marts     │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
   ┌─────────┐           ┌──────────┐          ┌───────────┐
   │ MLflow  │           │Streamlit │          │ Power BI  │
   │ XGBoost │           │ Web App  │          │ Dashboard │
   └─────────┘           └──────────┘          └───────────┘
```

---

⚙️ Layer-by-Layer Implementation

1️⃣ Infrastructure as Code — Terraform

Cloud resources are fully managed to guarantee immutable, drift-free deployments:

· providers.tf — Binds execution to GCP project usgs-511715 using HashiCorp Google provider ~> 5.0.
· main.tf — Declares the Earthquake_raw dataset (US multi-region, explicit retention) and the raw_usgs_data table with dynamic schema discovery on first load.

```hcl
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

Rationale: Anyone cloning the repo can reproduce the exact cloud environment with a single terraform apply. No manual clicking, no "works on my machine" drift.

---

2️⃣ Autonomous Ingestion & Deduplication — main.py

The Python ingestion service performs delta updates only, avoiding redundant writes:

· Time-Window Filtering — Fetches a rolling 24-hour USGS window (starttime/endtime) for events with magnitude ≥ 0.05.
· State Verification — Queries BigQuery over the last 2 days using TIMESTAMP_MILLIS(CAST(properties_time AS INT64)) to prevent duplicate id inserts.
· Complex Object Handling — Detects nested arrays in normalized columns and JSON-stringifies them before loading.

---

3️⃣ AI-Powered Self-Healing Agent — Gemini 2.5 Flash

Traditional ETL pipelines fail hard on schema drift. This engine recovers automatically:

· Failure Interception — Any pandas_gbq.to_gbq() schema/type exception is caught in a fallback try-except.
· Context Delivery — The agent receives the exact error traceback, current column list, and sample JSON rows.
· Structured Remediation — Gemini returns a strictly validated JSON instruction payload (stringify arrays, drop conflicting columns, etc.).
· In-Memory Healing & Retry — The DataFrame is transformed per the instructions and re-submitted to BigQuery — no human in the loop.

```python
try:
    pandas_gbq.to_gbq(df, destination_table=full_table_path, ...)
except Exception as bq_err:
    if "GEMINI_API_KEY" in os.environ:
        healed_df = ai_self_heal_data(df, str(bq_err))
        pandas_gbq.to_gbq(healed_df, destination_table=full_table_path, ...)
```

---

4️⃣ CI/CD Automation — GitHub Actions

A scheduled workflow provisions an ephemeral runner, installs dependencies, and executes ingestion — authenticated via encrypted repository secrets.

```text
[ Scheduler Trigger (cron + workflow_dispatch) ]
            │
            ▼
[ ubuntu-latest Ephemeral Runner ]
            │
            ▼
[ Python 3.12 + requirements.txt Install ]
            │
            ▼
[ main.py with GCP_SA_KEY + GEMINI_API_KEY ]
```

Operational Rationale:

· Credential Security — GCP_SA_KEY and GEMINI_API_KEY live in GitHub Secrets — never in code, never in .env committed to git.
· Zero Server Overhead — No VMs to patch, monitor, or pay for when idle.
· Realistic Cadence — GitHub's shared-runner queue means actual runs land every ~4–5 hours, perfectly matching USGS update patterns while preserving free-tier quotas.

---

5️⃣ Data Transformation — dbt Cloud

The dbt layer transforms semi-structured raw logs into a structured star schema ready for BI and ML.

```text
[ Earthquake_raw.raw_usgs_data ]  (Source)
              │
              ▼
     [ earthquake.sql ]           (Staging View: cast + coalesce)
              │
              ▼
 [ int_earthquake_enriched.sql ]  (Intermediate: coordinate parse, dedup, flags)
              │
     ┌────────┴────────┐
     ▼                 ▼
[ dim_earthquake_    [ fct_earthquake_
  location ]           events ]
```

Key Models:

· earthquake.yml — Source freshness: warns after 5 days, errors after 10 days of stale ingestion.
· earthquake.sql — Materialized view. Safe casting + COALESCE defaults protect downstream models from raw-schema drift.
· int_earthquake_enriched.sql — Parses geometry_coordinates JSON arrays into longitude/latitude/depth_km, deduplicates via row_number(), and derives business flags (magnitude severity, depth category, tsunami risk profile, pipeline latency).
· dim_earthquake_location.sql — Physical table: spatial attributes + country estimation for mapping tools.
· fct_earthquake_events.sql — Physical fact table: quantitative metrics, severity class, risk flag, latency.

Data Quality Tests (marts_test.yml):

· unique + not_null on earthquake_id
· relationships between fact and dimension
· accepted_values on severity class, depth category, and risk profile

Production Metrics:

· ✅ 84 successful dbt Cloud runs
· ✅ 100% job success rate
· ⏱ <1 minute average build time per cycle

---

6️⃣ Machine Learning — XGBoost + MLflow

Objective: Predict is_high_risk (magnitude ≥ 4.0) from historical seismic features.

Pipeline:

1. Extraction — SQL join of dim_earthquake_location + fct_earthquake_events for 8 key features (depth_km, latitude, longitude, magnitude, event_hour, total_stations_used, azimuthal_gap, significance_score).
2. Preprocessing — Stratified 80/20 split, StandardScaler normalization.
3. Training — XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.05).
4. Tracking — MLflow (SQLite backend) logs params, metrics, and model artifacts.

Results:

Metric Value
Dataset size 32,675 records
Features 8
ROC-AUC 1.0000
Accuracy 1.00
Precision / Recall / F1 1.00

⚠️ Note: Perfect scores on this baseline reflect that the target is derived directly from magnitude (which is itself a feature) — a documented design decision for establishing the end-to-end MLflow → BigQuery → model artifact plumbing. Future iterations will predict from independent seismic precursors to avoid target leakage.

---

7️⃣ Interactive Web App — Streamlit + Plotly

A SOC-style dark-themed analytics dashboard deployed on Streamlit Community Cloud.

Features:

· 🔐 Secure BigQuery Auth via st.secrets["GCP_SA_KEY"]
· ⚡ @st.cache_data(ttl=3600) — 1-hour caching to slash BQ query costs
· 🎛 Dynamic Filters — magnitude sliders + multi-select alert levels
· 📈 Real-Time KPIs — Total Events, Max/Avg Magnitude, Max/Avg Depth
· 🗺 Geospatial Map + Top-10 high-frequency seismic location table
· 📊 Plotly Analytics — Donut event-type breakdown, alert distribution, hourly + monthly trend charts

---

8️⃣ Executive BI — Power BI

An executive-grade dashboard connected to the BigQuery star-schema marts.

Layout:

· KPI Cards — Total Earthquakes, Avg Depth, Avg Magnitude, Avg Azimuthal Gap
· Temporal Trends — Monthly earthquake volume distribution (Jan → Dec)
· Geospatial Map — Latitude/longitude plot + country breakdown (Afghanistan, Alaska, …)
· Risk Matrix — Regional risk profiles × alert levels × significance scores

Purpose: Enable stakeholders to filter by severity, identify fault-line hotspots, and deploy emergency resources proactively — without writing SQL.

---

📂 Repository Structure

```text
USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/
├── .github/
│   └── workflows/
│       └── usgs_ingestion.yml       # Scheduled CI/CD ingestion workflow
├── ML/
│   └── train_model.py               # XGBoost + MLflow training pipeline
├── models/
│   └── Earthquake_usgs/             # dbt transformation models
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql
│       ├── marts/
│       │   ├── dim_earthquake_location.sql
│       │   └── fct_earthquake_events.sql
│       ├── earthquake.sql           # Staging view
│       ├── earthquake.yml           # Source config + freshness checks
│       └── marts_test.yml           # Data-quality tests
├── macros/                          # dbt custom macros
├── seeds/                           # Static seed data
├── snapshots/                       # SCD Type-2 snapshots
├── tests/                           # Custom dbt integrity tests
├── .gitignore
├── dbt_project.yml
├── main.py                          # Ingestion + Gemini self-healing agent
├── main.tf                          # BigQuery dataset & table (IaC)
├── providers.tf                     # GCP provider config
├── requirements.txt
├── usgs_python_dashboard.py         # Streamlit web app
└── README.md
```

---

🚀 Getting Started

Prerequisites

· Python 3.12+
· Terraform ≥ 1.5
· Google Cloud project with BigQuery API enabled
· GitHub account (for Actions)
· dbt Cloud account
· Gemini API key (Google AI Studio)

1. Clone & Install

```bash
git clone https://github.com/USERNAME/USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE.git
cd USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Provision Infrastructure

```bash
gcloud auth application-default login
cd terraform/
terraform init
terraform plan
terraform apply
```

3. Configure Secrets

Create a .env for local development (never commit this):

```env
GCP_SA_KEY={"type":"service_account", ...}
GEMINI_API_KEY=your_gemini_api_key
GCP_PROJECT_ID=usgs-511715
```

For GitHub Actions, add these in Settings → Secrets and variables → Actions:

Secret Purpose
GCP_SA_KEY Service account JSON for BigQuery write access
GEMINI_API_KEY Gemini 2.5 Flash self-healing agent

4. Run the Ingestion

```bash
python main.py
```

5. Run the dbt Transformation

```bash
dbt deps
dbt test
dbt run
```

6. Launch the Dashboard

```bash
streamlit run usgs_python_dashboard.py
```

7. Train the ML Model

```bash
python ML/train_model.py
mlflow ui   # view experiments at http://localhost:5000
```

---

🔐 Security & Secrets

· ✅ .env and *.json service account keys are in .gitignore
· ✅ Production credentials live exclusively in GitHub Secrets
· ✅ Streamlit Cloud uses st.secrets for GCP service-account auth
· ✅ BigQuery datasets are scoped to a dedicated GCP project (usgs-511715)
· ⚠️ Never commit real service-account JSON. Rotate keys immediately if leaked.

---

📊 Production Metrics at a Glance

Metric Value
dbt Cloud job success rate 100%
Completed dbt runs 84
Avg dbt build time < 1 min
ML dataset size 32,675 records
ML ROC-AUC 1.0000
Ingestion cadence ~4–5 hrs (GitHub Actions queue)
Pipeline downtime from schema drift 0 (AI self-healing)

---

🤝 Contributing

1. Fork the repository
2. Create a feature branch: git checkout -b feature/amazing-feature
3. Commit your changes: git commit -m "feat: add amazing feature"
4. Push: git push origin feature/amazing-feature
5. Open a Pull Request — all PRs must pass the CI workflow

---

📄 License

Distributed under the MIT License. See LICENSE for details.

---

👤 Author

[Your Name]

· GitHub: @USERNAME
· LinkedIn: linkedin.com/in/username
· Email: your@email.com

---

<div align="center">

⭐ If this project helped you, please consider giving it a star — it means a lot! ⭐

Built with precision, engineered for reliability, healed by AI.

</div>
```
