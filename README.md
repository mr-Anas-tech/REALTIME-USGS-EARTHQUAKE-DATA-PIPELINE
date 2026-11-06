🌍 USGS Global Seismic Intelligence Platform

End-to-End Cloud Data Engineering | Analytics Engineering | AI-Assisted Pipeline Recovery | Machine Learning | Business Intelligence

Technology stack: Python · Google Cloud · BigQuery · Terraform · Gemini 2.5 Flash · dbt · XGBoost · MLflow · Streamlit · Plotly · Power BI

---

📌 1. Project Overview

The USGS Global Seismic Intelligence Platform is an end-to-end cloud-based data engineering and analytics solution designed to collect, process, transform, and analyze earthquake telemetry published by the United States Geological Survey (USGS).

The platform transforms semi-structured GeoJSON earthquake records into structured, analytics-ready datasets through an integrated architecture combining:

- Infrastructure as Code (Terraform)
- Python-based data ingestion
- Google BigQuery data warehousing
- Gemini-powered AI-assisted recovery
- dbt analytics engineering
- XGBoost machine learning
- MLflow experiment tracking
- Streamlit and Plotly visualization
- Power BI executive reporting

The engineering challenge

Earthquake data is continuously updated and delivered through semi-structured API responses. Changes in source attributes, inconsistent data types, nested JSON structures, and repeated API records can introduce ingestion and transformation failures.

A conventional API-to-dashboard implementation does not adequately address these operational challenges.

This project explores a more resilient approach by introducing an AI-assisted recovery mechanism that uses Gemini 2.5 Flash to analyze ingestion errors and propose structured data corrections.

Proposed corrections are validated through deterministic application logic before they are applied.

What does the platform deliver?

Engineering Area| Implementation| Outcome
Infrastructure| Terraform + GCP| Reproducible cloud resources
Data ingestion| Python + Pandas| Automated API extraction
Data warehouse| Google BigQuery| Centralized analytical storage
AI-assisted recovery| Gemini 2.5 Flash| Structured error diagnosis
Orchestration| GitHub Actions| Scheduled ingestion execution
Transformation| dbt Cloud| Modular analytical models
Data quality| dbt tests + freshness| Validated analytical datasets
Machine learning| XGBoost| Threshold-based classification experiment
Experiment tracking| MLflow| Reproducible ML experiments
Application| Streamlit + Plotly| Interactive seismic exploration
Business intelligence| Power BI| Executive reporting

---

🏗️ 2. Platform Architecture

The platform follows a layered architecture that separates infrastructure, ingestion, storage, transformation, machine learning, and reporting.

High-level architecture

flowchart TD
    A["USGS Earthquake API"] --> B["Python Ingestion Engine"]

    B --> C["JSON Normalization"]
    C --> D["Data Validation"]
    D --> E["Deduplication"]

    E --> F["BigQuery Raw Warehouse"]

    E -->|Ingestion Failure| G["Gemini 2.5 Flash"]
    G --> H["Structured Repair Proposal"]
    H --> I["Validation and Allowlisted Repair"]
    I --> J["Controlled Retry"]
    J --> F

    K["Terraform / HCP Terraform"] --> L["GCP Infrastructure"]
    L --> F

    M["GitHub Actions"] --> B

    F --> N["dbt Staging"]
    N --> O["dbt Intermediate"]
    O --> P["Dimension Mart"]
    O --> Q["Fact Mart"]

    P --> R["XGBoost + MLflow"]
    Q --> R

    P --> S["Streamlit + Plotly"]
    Q --> S

    P --> T["Power BI"]
    Q --> T

Architecture principles

Separation of responsibilities: Infrastructure provisioning, ingestion, transformations, and reporting are maintained as distinct components.

Raw data preservation: Source data is stored independently from curated analytical models.

Centralized business logic: dbt provides reusable transformation logic rather than duplicating calculations across applications.

Controlled AI integration: Gemini proposes remediation actions, while deterministic Python validation controls execution.

Independent consumption: Machine learning, Streamlit, and Power BI consume curated warehouse models.

---

☁️ 3. Technology Stack

Technology| Responsibility| Why It Is Used
Python 3.12+| Data ingestion| API integration and data processing
Pandas| Data normalization| Converts nested JSON into tabular records
pandas-gbq| BigQuery loading| Transfers DataFrames into BigQuery
Google Cloud| Cloud infrastructure| Managed cloud environment
BigQuery| Data warehouse| Scalable analytical SQL processing
Terraform| Infrastructure as Code| Declarative resource provisioning
HCP Terraform Cloud| Terraform execution| Centralized infrastructure workflows, where configured
Gemini 2.5 Flash| AI-assisted recovery| Diagnoses data compatibility errors
GitHub Actions| Automation| Scheduled and manually triggered execution
dbt Cloud| Analytics engineering| Modular SQL transformations and tests
SQL| Data modeling| Warehouse-native analytical processing
XGBoost| Classification| Gradient-boosted tree model
MLflow| Experiment tracking| Records parameters, metrics, and artifacts
Streamlit| Application layer| Interactive Python web application
Plotly| Visualization| Interactive charts and maps
Power BI| Business intelligence| Executive analytics and reporting

---

🌎 4. Data Source — USGS Earthquake API

Primary provider: United States Geological Survey (USGS)

API documentation:
https://earthquake.usgs.gov/fdsnws/event/1/

GeoJSON feeds:
https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

The ingestion engine retrieves earthquake events through the USGS FDSN Event Web Service.

Extraction parameters

The current implementation uses the following extraction configuration:

Parameter| Purpose
"starttime"| Beginning of extraction window
"endtime"| End of extraction window
"minmagnitude"| Minimum earthquake magnitude
Response format| GeoJSON
Extraction window| Rolling 24-hour window
Minimum magnitude| 0.05

GeoJSON structure

USGS records contain two principal components.

Properties

- Event ID
- Magnitude
- Location description
- Event timestamp
- Updated timestamp
- Alert status
- Felt reports
- Significance score
- Station measurements

Geometry

- Geometry type
- Longitude
- Latitude
- Depth in kilometers

Why GeoJSON?

GeoJSON provides a standardized structure for geographical features and their attributes. It allows the platform to retain both seismic measurements and spatial coordinates for analytical processing.

---

⚙️ 5. Infrastructure as Code — Terraform & BigQuery

Infrastructure provisioning

The project uses Terraform to define and provision Google Cloud BigQuery resources.

Instead of manually creating warehouse resources through the cloud console, infrastructure definitions are maintained as version-controlled configuration files.

Why Terraform?

Manual provisioning can introduce inconsistent configurations, repetitive deployment work, and infrastructure drift.

Terraform provides declarative infrastructure management, making cloud resources easier to review, reproduce, and maintain.

Provisioned resources

Resource| Configuration| Purpose
GCP Project| "usgs-511715"| Cloud project
Dataset| "Earthquake_raw"| Raw telemetry storage
Table| "raw_usgs_data"| Incoming USGS records
Location| "US"| BigQuery multi-region

Terraform implementation

File: "main.tf"

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

File: "providers.tf"

The Google Terraform provider connects infrastructure execution to the target GCP project, using the configured Google provider version constraint of "~> 5.0".

Why BigQuery?

BigQuery provides managed analytical storage without requiring the project to maintain its own database servers.

It also supports:

- SQL-based transformations
- Large-scale analytical queries
- dbt integration
- Power BI connectivity
- Machine learning feature extraction

Schema consideration: Terraform provisions the warehouse resources, but it does not automatically guarantee compatibility with every future API schema change. Schema management must be handled through the ingestion and data validation process.

---

🐍 6. Python Data Ingestion Engine

Ingestion workflow

The Python ingestion engine retrieves earthquake records, normalizes GeoJSON responses, validates the resulting data, checks existing event IDs, and loads eligible records into BigQuery.

flowchart TD
    A["USGS REST API"] --> B["Fetch Recent Events"]
    B --> C["Parse GeoJSON"]
    C --> D["Normalize JSON Properties"]
    D --> E["Pandas DataFrame"]
    E --> F["Clean and Validate Columns"]
    F --> G["Query Existing Event IDs"]
    G --> H["Filter Previously Ingested Records"]
    H --> I["BigQuery Load"]

Data normalization

The ingestion engine converts semi-structured JSON objects into tabular DataFrame records.

Key operations include:

- Extracting event properties
- Standardizing column names
- Converting numerical fields
- Handling missing values
- Serializing nested structures where required
- Preparing geographical attributes
- Validating destination compatibility

Why normalization?

Raw API responses are designed for flexible data exchange, not direct analytical querying.

Normalization makes the data easier to store, validate, query, and transform through dbt.

Incremental ingestion and deduplication

The current implementation uses a rolling 24-hour extraction window and checks existing BigQuery event IDs across the previous two days.

The USGS event ID ("id") acts as the logical identifier.

Why deduplication?

Overlapping API extraction windows can repeatedly return previously collected records. Without deduplication, repeated records can inflate event counts and distort downstream aggregations.

The current event-ID filtering approach reduces this risk.

Future improvement: Use an event ID and source update timestamp with a BigQuery "MERGE" strategy. This would allow the platform to update previously collected records when USGS revises an event rather than simply skipping that event.

---

🤖 7. AI-Assisted Pipeline Recovery — Gemini 2.5 Flash

The problem

Data ingestion pipelines can fail when incoming API records no longer match the expected warehouse schema.

Examples include:

- Unexpected source columns
- Incompatible data types
- Nested arrays
- Unsupported values
- Schema mismatches

Traditional pipelines generally require developers to investigate these errors and manually modify their transformation logic.

The AI-assisted approach

This project integrates Gemini 2.5 Flash as an error-diagnosis and remediation assistant.

The model receives relevant diagnostic context and proposes structured corrections that can be validated by the Python application.

Recovery architecture

flowchart TD
    A["Pandas DataFrame"] --> B["BigQuery Write Attempt"]

    B -->|Success| C["Ingestion Completed"]
    B -->|Failure| D["Capture Exception"]

    D --> E["Collect Error and Schema Context"]
    E --> F["Gemini 2.5 Flash"]

    F --> G["JSON Repair Proposal"]
    G --> H["Validate Proposed Actions"]

    H -->|Approved| I["Apply In-Memory Repair"]
    H -->|Rejected| J["Log and Quarantine Failure"]

    I --> K["Controlled Retry"]

    K -->|Success| C
    K -->|Failure| J

Recovery stages

Stage 1 — Failure interception

The ingestion application catches exceptions raised during the BigQuery loading operation.

Stage 2 — Diagnostic context

The recovery process prepares relevant information:

- Error message
- DataFrame column names
- Data type information
- Representative records
- Destination schema information, where available

Stage 3 — AI-assisted diagnosis

Gemini analyzes the diagnostic context and returns a structured repair proposal.

Potential operations include:

- Serializing supported nested structures
- Converting compatible values
- Identifying conflicting columns
- Recommending permitted schema-compatible changes

Stage 4 — Validation and retry

The Python application validates the proposed instructions, applies permitted in-memory transformations, and attempts a controlled retry.

Why use AI-assisted recovery?

The purpose is to reduce repetitive manual troubleshooting and provide a flexible diagnostic mechanism for previously unseen data compatibility problems.

Production safety controls

AI-generated instructions must never be treated as automatically trustworthy.

A production implementation should enforce:

1. Strict JSON schema validation.
2. Explicit allowlisted operations.
3. Preservation of required business fields.
4. Row-count and schema validation.
5. Limited retry attempts.
6. Failed-record quarantine.
7. Audit logging.
8. Human approval for destructive or ambiguous changes.

Core principle: Gemini proposes a repair. Deterministic application logic validates and executes only permitted actions.

This is an AI-assisted recovery mechanism, not a guarantee of zero downtime or recovery from every possible failure.

---

🔄 8. Automated Ingestion — GitHub Actions

The project uses GitHub Actions to execute the Python ingestion workflow automatically.

Workflow capabilities

- Scheduled cron execution
- Manual execution using "workflow_dispatch"
- Ubuntu-hosted runners
- Python 3.12 environment
- Dependency installation
- Secure credential injection
- Automated execution of "main.py"

Execution architecture

flowchart TD
    A["GitHub Scheduler / Manual Trigger"] --> B["Ubuntu Hosted Runner"]
    B --> C["Checkout Repository"]
    C --> D["Configure Python"]
    D --> E["Install Dependencies"]
    E --> F["Load GitHub Secrets"]
    F --> G["Authenticate with GCP"]
    G --> H["Execute main.py"]
    H --> I["USGS Data Extraction"]
    I --> J["BigQuery Raw Dataset"]

Required GitHub Secrets

Secret| Purpose
"GCP_SA_KEY"| Google Cloud service account credentials
"GEMINI_API_KEY"| Gemini API authentication

Why GitHub Actions?

GitHub Actions removes the dependency on a continuously running local machine and provides a centralized environment for automated execution.

Execution model: The current implementation uses scheduled batch ingestion. GitHub Actions scheduling is not guaranteed to run at an exact minute, and this architecture should not be described as continuous streaming.

---

🧱 9. Analytics Engineering — dbt Cloud

Why dbt?

Raw seismic telemetry is not immediately suitable for analytical reporting.

The platform uses dbt to standardize raw data, centralize business logic, build reusable SQL models, and validate analytical datasets.

Data transformation layers

Layer| Responsibility| Purpose
Source| Raw USGS records| Preserve ingestion boundary
Staging| Standardization and casting| Consistent field definitions
Intermediate| Enrichment and business logic| Reusable transformations
Marts| Dimensions and facts| Business-ready datasets

dbt project structure

models/
└── Earthquake_usgs/
    ├── intermediate/
    │   └── int_earthquake_enriched.sql
    │
    ├── marts/
    │   ├── dim_earthquake_location.sql
    │   ├── fct_earthquake_events.sql
    │   └── marts_test.yml
    │
    ├── earthquake.sql
    └── earthquake.yml

dbt lineage

flowchart TD
    A["BigQuery Raw Table"]
    A --> B["earthquake.sql"]
    B --> C["int_earthquake_enriched.sql"]

    C --> D["dim_earthquake_location"]
    C --> E["fct_earthquake_events"]

    D --> F["Streamlit"]
    E --> F

    D --> G["Power BI"]
    E --> G

    D --> H["Machine Learning"]
    E --> H

9.1 Source freshness

File: "earthquake.yml"

The source configuration monitors the freshness of the raw BigQuery table.

version: 2

sources:
  - name: Earthquake_raw
    database: usgs-511715
    schema: Earthquake_raw

    tables:
      - name: raw_usgs_data
        config:
          loaded_at_field: >
            timestamp_millis(
              cast(properties_updated as int64)
            )

          freshness:
            warn_after:
              count: 5
              period: day

            error_after:
              count: 10
              period: day

Freshness policy

Condition| Threshold
Warning| 5 days
Error| 10 days

Why freshness monitoring?

A successful transformation does not necessarily mean the upstream data is current.

Freshness monitoring helps detect delayed source updates before stale data silently enters reporting.

The current configuration uses the source event update timestamp. A separate ingestion timestamp is recommended for measuring actual pipeline execution latency.

9.2 Staging model

File: "earthquake.sql"

The staging model standardizes raw USGS attributes into consistent analytical fields.

Representative SQL:

{{ config(materialized='view') }}

with raw_source as (

    select *
    from {{ source('Earthquake_raw', 'raw_usgs_data') }}

),

cleaned_eq as (

    select
        cast(id as string) as earthquake_id,

        cast(properties_type as string) as event_type,

        safe_cast(properties_mag as float64) as magnitude,

        coalesce(
            cast(properties_magType as string),
            'Unknown'
        ) as magnitude_type,

        cast(properties_place as string) as place_description,

        cast(properties_title as string) as event_title,

        cast(properties_status as string) as review_status,

        timestamp_millis(
            safe_cast(properties_time as int64)
        ) as event_timestamp,

        timestamp_millis(
            safe_cast(properties_updated as int64)
        ) as updated_timestamp,

        safe_cast(properties_felt as int64)
            as total_felt_reports,

        safe_cast(properties_cdi as float64)
            as max_reported_intensity,

        safe_cast(properties_mmi as float64)
            as instrumental_intensity,

        cast(properties_alert as string)
            as alert_level,

        safe_cast(properties_tsunami as int64)
            as tsunami_flag,

        safe_cast(properties_sig as int64)
            as significance_score,

        cast(properties_net as string)
            as network_id,

        cast(properties_code as string)
            as network_event_code,

        safe_cast(properties_nst as int64)
            as total_stations_used,

        safe_cast(properties_dmin as float64)
            as min_station_distance,

        safe_cast(properties_rms as float64)
            as rms_travel_time,

        safe_cast(properties_gap as float64)
            as azimuthal_gap,

        cast(geometry_type as string)
            as geometry_type,

        geometry_coordinates as coordinates_array

    from raw_source

)

select *
from cleaned_eq

Why safe casting?

"SAFE_CAST" returns NULL when a value cannot be converted to the expected type, rather than failing the entire query.

This helps isolate malformed values for further data-quality investigation.

Missing measurements should not automatically be converted to zero because a missing magnitude is not equivalent to a magnitude of zero.

9.3 Intermediate enrichment

File: "int_earthquake_enriched.sql"

The intermediate model centralizes geographical extraction, duplicate handling, event categorization, and analytical enrichment.

Key transformations:

Transformation| Analytical Purpose
Longitude extraction| Geographical visualization
Latitude extraction| Geographical visualization
Depth extraction| Depth analysis
Window functions| Duplicate selection
Magnitude classification| Event segmentation
Depth classification| Depth categorization
Event time extraction| Temporal reporting
Risk profile flags| Analytical segmentation
Reporting delay| Update timing analysis

Representative SQL:

with staging_data as (

    select *
    from {{ ref('earthquake') }}

),

extracted_coordinates as (

    select
        *,

        safe_cast(
            json_value(coordinates_array, '$[0]')
            as float64
        ) as longitude,

        safe_cast(
            json_value(coordinates_array, '$[1]')
            as float64
        ) as latitude,

        safe_cast(
            json_value(coordinates_array, '$[2]')
            as float64
        ) as depth_km,

        row_number() over (
            partition by earthquake_id
            order by
                updated_timestamp desc,
                event_timestamp desc
        ) as row_num

    from staging_data

),

insights as (

    select
        *,

        case
            when magnitude < 3.0
                then 'Micro/Minor (< 3.0)'

            when magnitude < 5.0
                then 'Light/Moderate (3.0 - 4.9)'

            when magnitude < 7.0
                then 'Strong (5.0 - 6.9)'

            else 'Major/Great (>= 7.0)'
        end as magnitude_severity_class,

        case
            when depth_km <= 70
                then 'Shallow (0-70 km)'

            when depth_km <= 300
                then 'Intermediate (70-300 km)'

            else 'Deep (> 300 km)'
        end as depth_category,

        extract(hour from event_timestamp)
            as event_hour,

        extract(dayofweek from event_timestamp)
            as event_day_of_week,

        format_timestamp('%B', event_timestamp)
            as event_month_name,

        timestamp_diff(
            updated_timestamp,
            event_timestamp,
            minute
        ) as pipeline_reporting_delay_minutes,

        case
            when tsunami_flag = 1 and magnitude >= 6.0
                then 'Critical High Risk'

            when tsunami_flag = 1 or magnitude >= 5.0
                then 'Elevated Risk'

            else 'Standard Monitoring'
        end as risk_profile_flag

    from extracted_coordinates

    where row_num = 1

)

select *
from insights

Implementation note: The coordinate extraction above assumes "coordinates_array" is stored in a JSON-compatible representation. If the BigQuery column is an actual repeated array, use the appropriate array indexing syntax instead of "JSON_VALUE".

Why intermediate modeling?

Centralizing complex business logic avoids duplicating transformations across multiple downstream models.

The intermediate layer improves consistency, reusability, and maintainability.

Analytical classification note

The "risk_profile_flag" is a project-defined analytical classification based on magnitude and the USGS tsunami flag.

It is not an official USGS warning, emergency response recommendation, or scientifically validated earthquake-danger prediction.

The geographical country/state attribute parsed from the USGS place description should also be treated as an estimate rather than authoritative reverse-geocoded geography.

9.4 Dimension and fact marts

"dim_earthquake_location"

Purpose: Store descriptive and geographical event attributes.

Attribute| Purpose
"earthquake_id"| Event identifier
"place_description"| Source location description
"event_title"| Event display name
"geometry_type"| GeoJSON geometry type
"longitude"| Geographic longitude
"latitude"| Geographic latitude
"depth_km"| Event depth
"depth_category"| Depth classification
Estimated location field| Descriptive geographical attribute

"fct_earthquake_events"

Purpose: Store measurable seismic event attributes and analytical classifications.

Attribute Group| Example Fields
Identifiers| "earthquake_id", "network_id"
Measurements| "magnitude", "significance_score"
Alert information| "alert_level", "risk_profile_flag"
Station information| "total_stations_used", "azimuthal_gap"
Intensity| "max_reported_intensity", "instrumental_intensity"
Temporal| "event_timestamp", "event_hour"
Operational| "updated_timestamp", "pipeline_reporting_delay_minutes"

Why separate dimensions and facts?

Dimensional modeling provides a clear structure for analytical queries and reporting.

Descriptive attributes are separated from measurable event records, making the warehouse easier for BI applications and analysts to consume.

9.5 Data quality testing

File: "marts_test.yml"

The project uses dbt tests to validate important analytical constraints.

Test| Purpose
"unique"| Detect duplicate identifiers
"not_null"| Validate required attributes
"accepted_values"| Validate predefined categories
"relationships"| Validate fact-to-dimension integrity

Representative YAML:

version: 2

models:

  - name: dim_earthquake_location
    description: "Geographical dimension containing earthquake locations."

    columns:
      - name: earthquake_id
        tests:
          - unique
          - not_null

      - name: depth_category
        tests:
          - accepted_values:
              arguments:
                values:
                  - 'Shallow (0-70 km)'
                  - 'Intermediate (70-300 km)'
                  - 'Deep (> 300 km)'

  - name: fct_earthquake_events
    description: "Fact table containing seismic event measurements."

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
        tests:
          - not_null

      - name: magnitude_severity_class
        tests:
          - accepted_values:
              arguments:
                values:
                  - 'Micro/Minor (< 3.0)'
                  - 'Light/Moderate (3.0 - 4.9)'
                  - 'Strong (5.0 - 6.9)'
                  - 'Major/Great (>= 7.0)'

      - name: risk_profile_flag
        tests:
          - accepted_values:
              arguments:
                values:
                  - 'Critical High Risk'
                  - 'Elevated Risk'
                  - 'Standard Monitoring'

Why automated testing?

A dashboard may look correct while displaying incomplete or duplicated records.

Automated tests provide measurable quality requirements before data is consumed by downstream applications.

Additional recommended checks include coordinate ranges, valid magnitude ranges, missing timestamps, and null geographical attributes.

9.6 dbt Cloud execution metrics

Operational Property| Recorded Value
Job name| "usgs_analytic_pipeline"
Environment| "usgs"
Completed runs| 84
Reported successful runs| 100%
Reported average execution| Under 1 minute

These are project-reported execution metrics from the observed reporting period, not independently audited production SLAs.

---

🧠 10. Machine Learning — XGBoost & MLflow

Objective

The platform includes a supervised machine learning experiment that extracts analytical attributes from BigQuery, prepares a modeling dataset, trains an XGBoost classifier, and records experiment metadata through MLflow.

Why XGBoost?

XGBoost is a gradient-boosted decision tree framework suitable for structured tabular datasets.

It supports nonlinear relationships, feature interactions, regularization, and configurable classification objectives.

ML architecture

flowchart TD
    A["BigQuery Analytical Marts"] --> B["Python Extraction"]
    B --> C["Feature Engineering"]
    C --> D["Data Cleaning"]
    D --> E["Train / Test Split"]
    E --> F["XGBoost Classifier"]
    F --> G["Model Evaluation"]
    G --> H["MLflow Tracking"]

    H --> I["Parameters"]
    H --> J["Metrics"]
    H --> K["Model Artifacts"]

Dataset configuration

The original experiment uses attributes including:

- Depth
- Latitude
- Longitude
- Magnitude
- Event hour
- Total seismic stations
- Azimuthal gap
- Additional selected event attributes

Target definition

The initial experiment defines:

is_high_risk = (df["magnitude"] >= 4.0).astype(int)

Target| Definition
0| Magnitude below 4.0
1| Magnitude equal to or above 4.0

Important: Target leakage

The original experiment includes magnitude among its input features, even though the target is directly calculated from magnitude.

This creates target leakage because the model can learn the threshold rule directly from the input rather than discover an independent predictive relationship.

Consequently, the initial reported ROC-AUC and classification metrics of 1.00 must not be interpreted as evidence of genuine predictive capability.

Recommended model improvement

For a meaningful evaluation:

1. Remove magnitude from the input features when predicting a magnitude-defined target.
2. Use chronological train/test splitting to evaluate future-event performance.
3. Compare the model with simple baseline classifiers.
4. Evaluate precision, recall, F1-score, ROC-AUC, and PR-AUC.
5. Investigate class imbalance.
6. Record configurations and metrics through MLflow.
7. Consider defining a scientifically meaningful future outcome.

Scope: This is a threshold-based seismic event classification experiment, not earthquake occurrence forecasting, earthquake timing prediction, or an operational early-warning system.

Initial experiment configuration

Parameter| Initial Value
Algorithm| XGBoost Classifier
"n_estimators"| 150
"max_depth"| 6
"learning_rate"| 0.05
Training split| 80%
Testing split| 20%
Split strategy| Stratified
Dataset records| 32,675
Initial features| 8
Tracking backend| MLflow SQLite

Why MLflow?

MLflow records experiment configurations and results, making it easier to compare model versions and reproduce earlier experiments.

The project uses MLflow for:

- Experiment history
- Hyperparameter tracking
- Evaluation metrics
- Model artifacts
- Reproducibility

---

📊 11. Interactive Application — Streamlit & Plotly

Application overview

The platform includes a Streamlit application that queries curated BigQuery dimension and fact marts to provide an interactive view of global seismic activity.

Application architecture

flowchart TD
    A["Streamlit Community Cloud"] --> B["BigQuery Authentication"]
    B --> C["Read Analytical Marts"]
    C --> D["Cached Data Layer"]
    D --> E["Interactive Filters"]

    E --> F["KPI Cards"]
    E --> G["Global Earthquake Map"]
    E --> H["Plotly Analytics"]
    E --> I["Event Tables"]

Technology components

- Streamlit
- Python
- Plotly
- Google BigQuery
- Streamlit Secrets
- Streamlit Community Cloud

Secure authentication

The application uses Streamlit Secrets to manage Google Cloud service account credentials.

Example:

st.secrets["GCP_SA_KEY"]

Credentials are kept outside the source code.

Data caching

@st.cache_data(ttl=3600)

The cache lifetime is one hour.

Why caching?

Repeated warehouse queries can increase execution costs and response times.

Caching reduces unnecessary repeated retrieval and improves application responsiveness.

Application features

Feature| Implementation| Purpose
Magnitude filtering| Interactive slider| Filter events by magnitude
Alert filtering| Selection controls| Explore alert categories
KPI cards| Streamlit metrics| Summarize selected records
Global map| Latitude and longitude| Explore spatial distribution
Top 10 locations| Ranking table| Identify frequently reported areas
Event distribution| Plotly donut chart| Compare event categories
Alert distribution| Plotly charts| Analyze alert classifications
Hourly trends| Time-series visualization| Explore hourly activity
Monthly trends| Temporal charts| Examine historical distributions

KPI monitoring

The application presents:

- Total seismic events
- Maximum magnitude
- Average magnitude
- Maximum depth
- Average depth

Geospatial exploration

The global map visualizes earthquake event coordinates.

Example geographical areas in the project include:

- Fiji region
- South Sandwich Islands
- Kermadec Islands

The geographical view helps users investigate spatial distributions and areas with higher reported event activity.

---

📈 12. Executive Business Intelligence — Power BI

Reporting objective

The platform includes an executive-oriented Power BI dashboard connected to BigQuery analytical marts.

The dashboard translates structured seismic information into accessible KPIs, geographical summaries, temporal trends, and analytical classifications.

Power BI architecture

flowchart TD
    A["dim_earthquake_location"] --> C["Power BI Data Model"]
    B["fct_earthquake_events"] --> C

    C --> D["Relationship: earthquake_id"]
    D --> E["Executive Dashboard"]

    E --> F["KPI Cards"]
    E --> G["Monthly Trends"]
    E --> H["Global Location Map"]
    E --> I["Risk and Alert Matrix"]

Dashboard components

A. Executive KPI cards

- Total earthquake events
- Average magnitude
- Average depth
- Average azimuthal gap

B. Temporal analysis

Monthly event volume provides a view of event frequency across calendar periods.

For meaningful seasonal analysis, year and month should be retained together rather than combining January records from multiple years into one category.

C. Geographical distribution

The report uses:

- Latitude
- Longitude
- Location descriptions
- Estimated country/state attributes

D. Risk and alert matrix

The dashboard includes project-defined analytical categories, available USGS alert levels, and significance scores.

These categories support analytical investigation and should not be interpreted as official emergency response instructions.

Why Power BI?

Power BI allows stakeholders to explore curated warehouse data through interactive reports without writing SQL.

It bridges the gap between technical data processing and business-oriented reporting.

---

🛡️ 13. Data Quality & Operational Reliability

Reliability is addressed throughout the data lifecycle rather than relying on a single validation step.

Layer| Validation Mechanism| Purpose
API ingestion| Payload normalization| Standardize incoming data
Python| Data type and column checks| Detect malformed records
Deduplication| Existing event ID checks| Reduce duplicate ingestion
AI recovery| Structured repair validation| Control automated corrections
BigQuery| Schema compatibility| Maintain storage consistency
dbt sources| Freshness monitoring| Detect stale data
dbt models| Type standardization| Improve analytical consistency
dbt tests| Uniqueness and integrity checks| Validate analytical constraints
ML workflow| Train/test evaluation| Assess model behavior
Dashboard| Query and filter logic| Support consistent reporting

Future reliability enhancements

- Explicit source schema contracts
- Failed-record quarantine tables
- Ingestion audit metadata
- Retry limits and exponential backoff
- Pipeline execution timestamps
- BigQuery "MERGE" for updated events
- Automated failure notifications
- Cross-layer data-quality monitoring

Why operational metadata?

The original event occurrence time, source update time, and actual platform ingestion time represent different operational events.

Recording all three makes it possible to measure ingestion latency and distinguish delayed source updates from pipeline execution failures.

---

🔐 14. Security & Credential Management

Component| Security Approach
Google Cloud| Dedicated service account
GitHub Actions| Encrypted repository secrets
Gemini| API key stored outside source code
Streamlit| Secrets management
Terraform| Protected infrastructure configuration
Repository| ".gitignore" for credentials and environment files

Security principles

- Never commit service account JSON files.
- Never expose API keys in source code.
- Apply least-privilege IAM permissions.
- Restrict service account access to required resources.
- Rotate credentials when necessary.
- Avoid sending unnecessary sensitive data to external AI services.
- Validate AI-generated transformations before execution.
- Protect Terraform state and its access credentials.

---

📁 15. Repository Structure

USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE/
│
├── .github/
│   └── workflows/
│       └── usgs_ingestion.yml
│
├── ML/
│   └── train_model.py
│
├── models/
│   └── Earthquake_usgs/
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql
│       │
│       ├── marts/
│       │   ├── dim_earthquake_location.sql
│       │   ├── fct_earthquake_events.sql
│       │   └── marts_test.yml
│       │
│       ├── earthquake.sql
│       └── earthquake.yml
│
├── macros/
├── seeds/
├── snapshots/
├── tests/
│
├── .gitignore
├── dbt_project.yml
├── main.py
├── main.tf
├── providers.tf
├── requirements.txt
├── usgs_python_dashboard.py
└── README.md

Core file responsibilities

File| Responsibility
"main.py"| API ingestion, normalization, deduplication, Gemini-assisted recovery
"main.tf"| BigQuery infrastructure provisioning
"providers.tf"| Terraform Google Cloud provider
"usgs_ingestion.yml"| GitHub Actions workflow
"earthquake.sql"| dbt staging transformation
"int_earthquake_enriched.sql"| Intermediate enrichment
"dim_earthquake_location.sql"| Geographical dimension
"fct_earthquake_events.sql"| Seismic event fact model
"marts_test.yml"| dbt data-quality tests
"train_model.py"| XGBoost training and MLflow tracking
"usgs_python_dashboard.py"| Streamlit application
"requirements.txt"| Python dependencies
"dbt_project.yml"| dbt project configuration

---

🚀 16. Deployment & Setup Guide

Prerequisites

- Python 3.12+
- Google Cloud account
- BigQuery enabled
- Google Cloud service account
- Terraform CLI
- HCP Terraform Cloud configuration, if used
- Gemini API key
- GitHub account
- dbt Cloud account
- Streamlit Community Cloud account
- Power BI Desktop

Step 1 — Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>

cd USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE

Replace the placeholder with the actual repository URL.

Step 2 — Create a Python environment

python -m venv venv

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Step 3 — Configure credentials

Configure Google Cloud authentication using a service account with the minimum required permissions.

Required configuration:

GCP_SA_KEY
GEMINI_API_KEY

Do not commit real credentials or ".env" files to the repository.

Step 4 — Provision infrastructure

terraform init
terraform validate
terraform plan
terraform apply

Review the proposed infrastructure changes before applying them.

Step 5 — Execute ingestion

python main.py

Verify that records are loaded into:

Earthquake_raw.raw_usgs_data

Step 6 — Configure dbt

Configure the BigQuery connection in dbt Cloud.

Typical validation and execution commands:

dbt debug
dbt source freshness
dbt run
dbt test

Step 7 — Train the ML model

python ML/train_model.py

Verify experiment parameters, metrics, and artifacts in MLflow.

Step 8 — Launch Streamlit

streamlit run usgs_python_dashboard.py

Configure the deployed application with the required Streamlit Secrets.

Step 9 — Configure Power BI

Connect Power BI to the BigQuery analytical marts.

Configure and validate the relationship between the dimension and fact tables using "earthquake_id".

---

📊 17. Project Performance & Recorded Metrics

The following values represent the reported implementation and execution history.

Metric| Recorded Value
Historical ML dataset records| 32,675
Initial ML feature attributes| 8
XGBoost estimators| 150
Completed dbt runs| 84
Reported dbt success rate| 100%
Average dbt execution| Under 1 minute
Source freshness warning| 5 days
Source freshness error| 10 days
Streamlit cache lifetime| 1 hour

ML evaluation qualification: The original experiment reported ROC-AUC and classification metrics of 1.00. Because the target is derived from magnitude and magnitude was included among the input features, those metrics are not validated predictive results.

A leakage-free evaluation is required before publishing corrected performance metrics.

These are project-reported measurements, not independently audited production SLAs.

---

🧩 18. Engineering Challenges & Solutions

Challenge| Implemented Approach| Engineering Value
Semi-structured GeoJSON| Pandas normalization| Converts API payloads into tabular data
Nested geographical arrays| JSON handling and coordinate extraction| Supports spatial analysis
Duplicate API responses| BigQuery event ID verification| Protects aggregate accuracy
Schema incompatibilities| Gemini-assisted diagnosis| Reduces manual troubleshooting
Inconsistent analytical fields| dbt staging models| Establishes standard definitions
Complex business logic| Intermediate SQL models| Improves transformation reuse
Data integrity| dbt automated tests| Detects analytical inconsistencies
Repeated warehouse queries| Streamlit caching| Reduces unnecessary retrieval
Experiment reproducibility| MLflow| Maintains model history
Executive reporting| Power BI| Makes analytics accessible

---

🛣️ 19. Limitations & Future Roadmap

The current implementation establishes a foundation for further engineering improvements.

Area| Future Enhancement| Expected Benefit
Streaming ingestion| Google Pub/Sub + Dataflow| Lower-latency processing
Cloud execution| Cloud Run| Managed ingestion execution
Orchestration| Cloud Composer / Airflow| Advanced dependency management
Data modeling| Incremental dbt models| More efficient transformations
Schema management| Versioned schema contracts| Safer schema evolution
AI recovery| Validated repair policies| Controlled automation
Data quality| Additional dbt tests / Great Expectations| Broader validation
Machine learning| Leakage-free temporal evaluation| More meaningful model assessment
MLOps| MLflow Model Registry| Model lifecycle management
Monitoring| Cloud Logging and alerting| Better operational visibility
Infrastructure| Terraform modules and remote state| Infrastructure governance
Warehouse optimization| Partitioning and clustering| More efficient queries

Long-term architecture

The next architectural iteration can evolve from scheduled batch ingestion toward event-driven processing.

flowchart TD
    A["USGS Event API"] --> B["Cloud Run Ingestion"]
    B --> C["Google Pub/Sub"]
    C --> D["Dataflow Processing"]
    D --> E["BigQuery Raw Layer"]
    E --> F["dbt Transformations"]
    F --> G["Analytical Marts"]

    G --> H["MLflow + ML Models"]
    G --> I["Streamlit"]
    G --> J["Power BI"]

    K["Cloud Monitoring"] --> B
    K --> C
    K --> D

This is a proposed future architecture, not the current implementation.

Why event-driven processing?

Scheduled batch processing is appropriate for periodic data collection. Event-driven processing can reduce latency and improve responsiveness when events need to be processed more frequently.

---

💼 20. Business & Analytical Value

The platform is designed to convert publicly available seismic telemetry into structured and accessible analytical information.

Its value extends beyond collecting earthquake records.

It provides an integrated workflow for:

- Centralizing seismic event information
- Standardizing geographical and numerical attributes
- Improving ingestion resilience
- Monitoring source freshness
- Validating analytical data quality
- Segmenting events through defined classifications
- Exploring geographical activity patterns
- Tracking machine learning experiments
- Communicating findings through interactive reporting

Stakeholder value

Stakeholder| Potential Value
Data Engineers| Automated ingestion and cloud infrastructure
Analytics Engineers| Modular dbt transformations and tested marts
Data Analysts| Query-ready seismic datasets
Researchers| Geographical and temporal exploration
Business stakeholders| Executive KPIs and reporting
ML practitioners| Structured feature datasets and experiment tracking

Scope limitation: This is an analytical monitoring and research platform. It does not replace official earthquake early-warning systems, geological hazard assessments, or emergency response authorities.

---

📚 21. Data Sources & Technical References

Primary data provider

United States Geological Survey (USGS)

- "USGS Earthquake Hazards Program" (https://earthquake.usgs.gov/)
- "USGS FDSN Event Web Service" (https://earthquake.usgs.gov/fdsnws/event/1/)
- "USGS GeoJSON Feeds" (https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)

Technology documentation

- "Google BigQuery" (https://cloud.google.com/bigquery/docs)
- "Terraform Google Provider" (https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- "Gemini API" (https://ai.google.dev/gemini-api/docs)
- "dbt Documentation" (https://docs.getdbt.com/)
- "GitHub Actions" (https://docs.github.com/actions)
- "XGBoost" (https://xgboost.readthedocs.io/)
- "MLflow" (https://mlflow.org/docs/latest/)
- "Streamlit" (https://docs.streamlit.io/)
- "Plotly" (https://plotly.com/python/)
- "Power BI" (https://learn.microsoft.com/power-bi/)

---

🖥️ 22. Project Links & Visual Demonstration

Resource| Link
GitHub Repository| Add your actual repository URL
Live Streamlit Application| Add your deployed application URL
Power BI Report| Add your published report URL, if available
Architecture Diagram| Add your diagram URL, if available

Application screenshots

Create the following directory in your repository:

docs/
└── images/
    ├── streamlit_dashboard.png
    ├── powerbi_dashboard.png
    ├── mlflow_experiments.png
    └── architecture.png

Once the screenshots have been committed, add these image references to the README:

Streamlit — Global Seismic Monitoring

![Streamlit Dashboard](docs/images/streamlit_dashboard.png)

Power BI — Executive Analytics

![Power BI Dashboard](docs/images/powerbi_dashboard.png)

MLflow — Experiment Tracking

![MLflow Experiments](docs/images/mlflow_experiments.png)

Platform Architecture

![Platform Architecture](docs/images/architecture.png)

Only add these image references after the corresponding image files exist in the repository. Otherwise, GitHub will display broken image references.

---

🎯 23. Conclusion

The USGS Global Seismic Intelligence Platform demonstrates an integrated approach to modern cloud data engineering and analytics.

It combines Terraform-based infrastructure provisioning, Python ingestion, Gemini-assisted recovery, BigQuery warehousing, dbt analytics engineering, XGBoost experimentation, MLflow tracking, Streamlit application development, and Power BI reporting.

The architecture emphasizes modularity, automation, data quality, maintainability, and responsible AI integration.

More importantly, the project demonstrates how multiple engineering disciplines can work together to transform an external data source into a structured analytical platform.

The ultimate objective is to transform raw global seismic telemetry into reliable, structured, and accessible intelligence.

---

👨‍💻 Author & Project Ownership

Developed as an independent end-to-end data engineering and analytics project.

Technology stack:

Python | SQL | Terraform | Google Cloud | BigQuery | Gemini AI | dbt | GitHub Actions | XGBoost | MLflow | Streamlit | Plotly | Power BI

Built to explore the intersection of Data Engineering, Analytics Engineering, AI-assisted automation, Machine Learning, and Business Intelligence.

---

From Raw Seismic Data to Analytical Intelligence.
