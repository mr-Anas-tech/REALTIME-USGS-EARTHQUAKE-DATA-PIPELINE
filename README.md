# 🌍 USGS Global Seismic Activity Tracker & AI Self-Healing Pipeline

An enterprise-grade, cloud-native Analytics Engineering platform that ingests, transforms, models, and predicts global earthquake telemetry from the United States Geological Survey (USGS). Powered by an AI self-healing ingestion engine that eliminates pipeline downtime caused by schema drift.

![Ingestion Workflow](https://github.com/USERNAME/USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/actions/workflows/usgs_ingestion.yml/badge.svg)
![dbt](https://img.shields.io/badge/dbt-Cloud-FF694B)
![BigQuery](https://img.shields.io/badge/BigQuery-Google_Cloud-4285F4)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 Executive Summary

Traditional ETL pipelines are brittle. A single upstream schema change or unexpected data-type drift can halt critical ingestion, silently breaking dashboards, ML models, and downstream reporting for hours.

This platform was engineered to solve that problem. It ingests real-time global seismic telemetry from the USGS public API and pairs Google BigQuery, Terraform, and dbt Cloud with an AI-powered self-healing agent (Gemini 2.5 Flash) that detects schema drift and type-mismatch failures mid-execution, auto-remediates malformed records in memory, and resumes writes to BigQuery without human intervention.

The result is a zero-downtime, fully observable, end-to-end analytics platform spanning ingestion, transformation, ML prediction, and executive BI.

---

## 🎯 Key Capabilities

| Capability | Description |
| :--- | :--- |
| **Autonomous Ingestion** | Scheduled GitHub Actions runs every 4 to 5 hours, polling a rolling 24-hour USGS window with deduplication against BigQuery state. |
| **AI Self-Healing** | Gemini 2.5 Flash receives live error tracebacks, inspects payloads, and returns validated JSON repair instructions executed in-memory before retry. |
| **Immutable Infrastructure** | Terraform provisions BigQuery datasets and tables declaratively. No manual console clicks, no configuration drift. |
| **Modular dbt Modeling** | Staging, Intermediate, and Dimension/Fact star schema with source freshness monitoring and automated data-quality tests. |
| **ML Prediction** | XGBoost binary classifier for high-risk event detection, experiment-tracked end-to-end via MLflow. |
| **Interactive Dashboard** | Streamlit SOC-style dark web app with real-time filters, KPI cards, geospatial map, and Plotly analytics. |
| **Executive BI** | Power BI dark-mode command-center dashboard for stakeholders, emergency response, and regional planners. |

---

## 🛠 Tech Stack & Engineering Rationale

| Layer | Technology | Why It Was Chosen |
| :--- | :--- | :--- |
| Infrastructure | HCP Terraform Cloud | Declarative, reproducible cloud provisioning. Eliminates manual setup and ensures identical environments across teams. |
| Data Warehouse | Google BigQuery | Serverless, columnar, sub-second queries at petabyte scale. Zero infrastructure management for high-throughput ingestion. |
| Ingestion Engine | Python 3.12 + Pandas + pandas-gbq | Mature REST and JSON handling, memory-efficient bulk streaming into BigQuery via modern drivers. |
| AI Remediation | Google GenAI SDK (gemini-2.5-flash) | Automated fallback agent. Inspects error tracebacks and payload samples, returns structured repair instructions with low latency. |
| Orchestration (CI/CD) | GitHub Actions | Serverless scheduling, encrypted secret management, zero-cost runners for public repos. |
| Transformation | dbt Cloud | Modular SQL modeling, built-in tests, source freshness, and scheduled job orchestration with full lineage. |
| ML Training | XGBoost + MLflow | Best-in-class tabular performance plus reproducible experiment tracking with artifact versioning. |
| Web App | Streamlit + Plotly | Rapid deployment of interactive, cache-backed analytics with SOC-grade dark theming. |
| BI Reporting | Power BI | Executive-ready visuals with native BigQuery connectivity and row-level security. |

---

## 📐 System Architecture

The platform flows in six stages. First, the USGS public REST API returns real-time GeoJSON telemetry. Second, the Python ingestion engine normalizes JSON, cleans columns, and deduplicates against BigQuery. Third, the engine attempts a BigQuery write. If successful, the raw dataset is populated. If it fails due to schema drift, Gemini 2.5 Flash inspects the traceback, repairs the DataFrame in memory, and retries. Fourth, dbt Cloud transforms raw data into a star schema. Fifth, the data powers an ML pipeline (XGBoost trained via MLflow) that predicts high-risk events. Sixth, outputs feed both a Streamlit web app and a Power BI executive dashboard.

```
USGS API → Python Ingestion → BigQuery Raw → dbt Models → Star Schema
                                    ↑              │
                                    │              ▼
                          Gemini Self-Heal    MLflow / XGBoost
                                    │              │
                                    │              ▼
                                    └──────── Streamlit + Power BI
```

---

## ⚙ Layer-by-Layer Implementation

### 1. Infrastructure as Code (Terraform)

Cloud resources are fully managed to guarantee immutable, drift-free deployments. The `providers.tf` file binds execution to GCP project `usgs-511715` using HashiCorp Google provider version constraint `~> 5.0`. The `main.tf` file declares the `Earthquake_raw` dataset with US multi-region location and the `raw_usgs_data` table with dynamic schema discovery on first load.

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

**Rationale:** Anyone cloning the repo can reproduce the exact cloud environment with a single `terraform apply`. No manual clicking, no environment drift.

---

### 2. Autonomous Ingestion and Deduplication (main.py)

The Python ingestion service performs delta updates only, avoiding redundant writes.

- **Time-window filtering:** fetches a rolling 24-hour USGS window using `starttime` and `endtime` parameters for events with magnitude greater than or equal to 0.05.
- **State verification:** queries BigQuery over the last 2 days using `TIMESTAMP_MILLIS(CAST(properties_time AS INT64))` to prevent duplicate primary key (id) inserts.
- **Complex object handling:** detects nested arrays in normalized columns and JSON-stringifies them before loading.

---

### 3. AI-Powered Self-Healing Agent (Gemini 2.5 Flash)

Traditional ETL pipelines fail hard on schema drift. This engine recovers automatically.

- **Failure interception:** any `pandas_gbq.to_gbq()` schema or type exception is caught in a fallback try-except block.
- **Context delivery:** the agent receives the exact error traceback, current column list, and sample JSON rows.
- **Structured remediation:** Gemini returns a strictly validated JSON instruction payload indicating repair steps such as stringifying unhandled arrays or dropping conflicting columns.
- **In-memory healing and retry:** the DataFrame is transformed per the instructions and re-submitted to BigQuery without human intervention.

```python
try:
    pandas_gbq.to_gbq(df, destination_table=full_table_path, ...)
except Exception as bq_err:
    if "GEMINI_API_KEY" in os.environ:
        healed_df = ai_self_heal_data(df, str(bq_err))
        pandas_gbq.to_gbq(healed_df, destination_table=full_table_path, ...)
```

---

### 4. CI/CD Automation (GitHub Actions)

A scheduled workflow provisions an ephemeral runner, installs dependencies, and executes ingestion, authenticated via encrypted repository secrets.

- **Scheduler trigger:** cron schedule plus manual `workflow_dispatch` support.
- **Runner environment:** `ubuntu-latest` ephemeral virtual machine.
- **Secure setup:** Python 3.12 runtime with requirements installation.
- **Autonomous run:** main.py injected with `GCP_SA_KEY` and `GEMINI_API_KEY` secrets.

**Operational rationale:**

- **Credential security:** GCP and Gemini keys live in GitHub Secrets, never in code and never in committed `.env` files.
- **Zero server overhead:** no VMs to patch, monitor, or pay for when idle.
- **Realistic cadence:** GitHub shared-runner queue means actual runs land every 4 to 5 hours, perfectly matching USGS update patterns while preserving free-tier quotas.

---

### 5. Data Transformation (dbt Cloud)

The dbt layer transforms semi-structured raw logs into a structured star schema ready for BI and ML.

**Source freshness (`earthquake.yml`):** monitors update freshness. Warns after 5 days, errors after 10 days of stale ingestion.

**Staging model (`earthquake.sql`):** materialized as a lightweight view over the raw source. Standardizes column names, applies safe type casting, and COALESCE defaults to missing telemetry.

**Intermediate model (`int_earthquake_enriched.sql`):** extracts longitude, latitude, and depth from `geometry_coordinates` JSON arrays, deduplicates via `row_number()`, and derives business flags including magnitude severity class, depth category, tsunami risk profile, and pipeline reporting delay.

**Data marts:**

- `dim_earthquake_location.sql` - physical table containing spatial attributes, precise coordinates, and depth categories for mapping tools.
- `fct_earthquake_events.sql` - physical fact table capturing quantitative metrics, magnitude classes, risk profile flags, and pipeline latency metrics.

**Data quality tests (`marts_test.yml`):**

- `unique` and `not_null` on `earthquake_id`
- `relationships` between fact and dimension
- `accepted_values` on severity class, depth category, and risk profile

**Production metrics:**

- 100% dbt Cloud job success rate
- 84 completed runs
- Average build time under 1 minute per cycle

---

### 6. Machine Learning (XGBoost and MLflow)

**Objective:** predict `is_high_risk` (magnitude greater than or equal to 4.0) from historical seismic features.

**Pipeline steps:**

1. **Extraction:** SQL join of `dim_earthquake_location` and `fct_earthquake_events` for 8 key features including `depth_km`, `latitude`, `longitude`, `magnitude`, `event_hour`, `total_stations_used`, `azimuthal_gap`, and `significance_score`.
2. **Preprocessing:** stratified 80/20 split, `StandardScaler` normalization.
3. **Training:** `XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.05)`.
4. **Tracking:** MLflow with SQLite backend logs params, metrics, and model artifacts.

**Results:**

| Metric | Value |
| :--- | :--- |
| Dataset size | 32,675 records |
| Features | 8 |
| ROC-AUC | 1.0000 |
| Accuracy | 1.00 |
| Precision / Recall / F1 | 1.00 |

> **Note on model scores:** the target is derived directly from `magnitude`, which is also included as a feature. Perfect scores therefore reflect a clean boundary rather than true generalization. This baseline establishes the end-to-end MLflow to BigQuery to model artifact plumbing. Future iterations will predict from independent seismic precursors to avoid target leakage.

---

### 7. Interactive Web App (Streamlit and Plotly)

A SOC-style dark-themed analytics dashboard deployed on Streamlit Community Cloud.

**Features:**

- Secure BigQuery auth via `st.secrets["GCP_SA_KEY"]`
- `@st.cache_data(ttl=3600)` caching that reduces BigQuery query costs and provides instant dashboard load times
- Dynamic filters including magnitude sliders and multi-select alert levels
- Real-time KPIs showing Total Events, Max and Avg Magnitude, Max and Avg Depth
- Geospatial map plus a Top-10 high-frequency seismic location table
- Plotly analytics including donut event-type breakdown, alert distribution, hourly rates, and monthly trend charts

---

### 8. Executive BI (Power BI)

An executive-grade dashboard connected to the BigQuery star-schema marts.

**Layout components:**

- **KPI cards:** Total Earthquakes, Avg Depth, Avg Magnitude, Avg Azimuthal Gap.
- **Temporal trends:** monthly earthquake volume distribution from January through December.
- **Geospatial map:** latitude and longitude plot with country breakdown.
- **Risk matrix:** regional risk profiles by alert level and significance score.

**Purpose:** enable stakeholders to filter by severity, identify fault-line hotspots, and deploy emergency resources proactively without writing SQL.

---

## 📂 Repository Structure

```
USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/
├── .github/
│   └── workflows/
│       └── usgs_ingestion.yml
├── ML/
│   └── train_model.py
├── models/
│   └── Earthquake_usgs/
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql
│       ├── marts/
│       │   ├── dim_earthquake_location.sql
│       │   └── fct_earthquake_events.sql
│       ├── earthquake.sql
│       ├── earthquake.yml
│       └── marts_test.yml
├── macros/
├── seeds/
├── snapshots/
├── tests/
├── .gitignore
├── dbt_project.yml
├── main.py
├── main.tf
├── providers.tf
├── requirements.txt
├── usgs_python_dashboard.py
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Terraform version 1.5 or higher
- Google Cloud project with BigQuery API enabled
- GitHub account for Actions
- dbt Cloud account
- Gemini API key from Google AI Studio

### 1. Clone and install

```bash
git clone https://github.com/USERNAME/USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE.git
cd USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Provision infrastructure

```bash
gcloud auth application-default login
cd terraform/
terraform init
terraform plan
terraform apply
```

### 3. Configure secrets

Create a `.env` file for local development. Never commit this file.

```env
GCP_SA_KEY={"type":"service_account", ...}
GEMINI_API_KEY=your_gemini_api_key
GCP_PROJECT_ID=usgs-511715
```

For GitHub Actions, add these in Settings, Secrets and variables, Actions:

| Secret | Purpose |
| :--- | :--- |
| GCP_SA_KEY | Service account JSON for BigQuery write access |
| GEMINI_API_KEY | Gemini 2.5 Flash self-healing agent |

### 4. Run ingestion

```bash
python main.py
```

### 5. Run dbt transformation

```bash
dbt deps
dbt test
dbt run
```

### 6. Launch the dashboard

```bash
streamlit run usgs_python_dashboard.py
```

### 7. Train the ML model

```bash
python ML/train_model.py
mlflow ui
```

---

## 🔐 Security and Secrets

- `.env` and `*.json` service account keys are listed in `.gitignore`
- Production credentials live exclusively in GitHub Secrets
- Streamlit Cloud uses `st.secrets` for GCP service account auth
- BigQuery datasets are scoped to a dedicated GCP project (`usgs-511715`)
- Never commit real service account JSON. Rotate keys immediately if leaked.

---

## 📊 Production Metrics at a Glance

| Metric | Value |
| :--- | :--- |
| dbt Cloud job success rate | 100% |
| Completed dbt runs | 84 |
| Average dbt build time | Under 1 minute |
| ML dataset size | 32,675 records |
| ML ROC-AUC | 1.0000 |
| Ingestion cadence | Every 4 to 5 hours |
| Pipeline downtime from schema drift | Zero (AI self-healing) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "feat: add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request. All PRs must pass the CI workflow.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 👤 Author


- Name: Muhammad Anas
- GitHub: [@USERNAME](https://github.com/mr-Anas-tech)
- LinkedIn: [linkedin.com/in/username](https://www.linkedin.com/in/muhammad-anas-5795923a9?utm_source=share_via&utm_content=profile&utm_medium=member_android)
- Email: mranaskhudabukh@gmail.com

---

If this project helped you, please consider giving it a star.
