🌍 USGS Global Seismic Intelligence Platform

Cloud-Native Data Engineering | Analytics Engineering | AI-Assisted Pipeline Recovery | Machine Learning | Business Intelligence

""Python" (https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)" (https://www.python.org/)
""Google BigQuery" (https://img.shields.io/badge/Google%20BigQuery-Data%20Warehouse-4285F4?logo=googlebigquery&logoColor=white)" (https://cloud.google.com/bigquery)
""Terraform" (https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform&logoColor=white)" (https://developer.hashicorp.com/terraform)
""dbt" (https://img.shields.io/badge/dbt-Analytics%20Engineering-FF694B?logo=dbt&logoColor=white)" (https://www.getdbt.com/)
""Gemini AI" (https://img.shields.io/badge/Gemini-AI%20Recovery-8E75B2?logo=googlegemini&logoColor=white)" (https://ai.google.dev/)
""XGBoost" (https://img.shields.io/badge/XGBoost-Machine%20Learning-EC6C26)" (https://xgboost.ai/)
""MLflow" (https://img.shields.io/badge/MLflow-Experiment%20Tracking-0194E2?logo=mlflow&logoColor=white)" (https://mlflow.org/)
""Streamlit" (https://img.shields.io/badge/Streamlit-Interactive%20Analytics-FF4B4B?logo=streamlit&logoColor=white)" (https://streamlit.io/)
""Power BI" (https://img.shields.io/badge/Power%20BI-Executive%20Analytics-F2C811?logo=powerbi&logoColor=black)" (https://powerbi.microsoft.com/)

---

1. Project Overview

The USGS Global Seismic Intelligence Platform is a cloud-native data engineering and analytics solution designed to ingest, process, transform, and analyze global earthquake telemetry provided by the United States Geological Survey (USGS).

The platform transforms semi-structured GeoJSON earthquake events into structured, analytics-ready datasets through an integrated architecture combining Infrastructure as Code (IaC), automated ingestion, AI-assisted error recovery, analytics engineering, machine learning, and interactive business intelligence.

Unlike a conventional API-to-dashboard implementation, this project introduces an AI-assisted self-healing mechanism that uses Google's Gemini 2.5 Flash model to inspect ingestion failures, identify potential schema and data-type incompatibilities, and propose structured in-memory data corrections before retrying failed BigQuery writes.

The resulting data is modeled through dbt into dimensional and fact tables, evaluated through an XGBoost classification workflow, and exposed through interactive Streamlit and Power BI reporting interfaces.

The engineering problem

Earthquake telemetry is continuously updated, semi-structured, and potentially inconsistent across incoming API responses. A conventional ingestion pipeline can encounter:

- Unexpected or newly introduced source attributes.
- Inconsistent data types across JSON records.
- Nested arrays and complex GeoJSON structures.
- Duplicate events during overlapping ingestion windows.
- Invalid or missing analytical attributes.
- Downstream transformation failures caused by upstream schema changes.

These issues can compromise data quality, interrupt ingestion, and increase operational maintenance.

The proposed solution

The platform addresses these challenges through five engineering principles:

1. Infrastructure automation: Provision BigQuery resources declaratively using Terraform.
2. Resilient ingestion: Automate API extraction, normalization, deduplication, and warehouse loading using Python.
3. AI-assisted recovery: Use Gemini to diagnose ingestion errors and propose controlled data repairs.
4. Reliable analytical modeling: Implement modular dbt transformations, freshness monitoring, and automated data tests.
5. Decision-oriented analytics: Deliver machine learning experiments, geospatial monitoring, and executive BI reporting.

Project objectives

Objective| Engineering implementation| Expected value
Automated infrastructure| Terraform + BigQuery| Reproducible cloud environments
Reliable ingestion| Python + Pandas| Consistent data collection
Failure recovery| Gemini 2.5 Flash| Reduced manual troubleshooting
Data standardization| dbt| Reusable analytical models
Data quality| dbt tests + freshness| Improved analytical reliability
Predictive classification| XGBoost + MLflow| Reproducible ML experiments
Interactive analytics| Streamlit + Plotly| Accessible seismic exploration
Executive reporting| Power BI| Business-oriented decision support

---

2. Key Platform Capabilities

Capability| Implementation| Purpose
Automated cloud provisioning| HCP Terraform Cloud| Infrastructure consistency
Global seismic ingestion| USGS GeoJSON API| Collect earthquake telemetry
Dynamic JSON normalization| Python + Pandas| Standardize semi-structured data
Duplicate prevention| BigQuery SQL + Python| Avoid repeated event ingestion
AI-assisted recovery| Gemini 2.5 Flash| Diagnose and repair compatible ingestion errors
Data warehousing| Google BigQuery| Centralized analytical storage
Scheduled orchestration| GitHub Actions| Automated ingestion execution
Transformation| dbt Cloud| Modular analytical data modeling
Data quality| dbt tests| Validate critical data constraints
Experiment tracking| MLflow| Reproducible model experiments
Classification| XGBoost| Classify threshold-defined seismic events
Interactive analytics| Streamlit + Plotly| Explore global earthquake activity
Executive BI| Power BI| Monitor operational metrics

---

3. Technology Stack & Engineering Rationale

The technology selection is based on architectural responsibilities, scalability, maintainability, and the practical requirements of an end-to-end analytical platform.

Technology| Architectural responsibility| Why this technology?| Engineering / business value
HCP Terraform Cloud| Infrastructure as Code| Declarative resource management provides consistent infrastructure definitions.| Reduces manual configuration and infrastructure drift.
Google Cloud Platform| Cloud infrastructure| Provides managed cloud services for data storage and analytical workloads.| Reduces infrastructure administration.
BigQuery| Data warehouse| Serverless analytical storage supports SQL-based processing at scale.| Centralizes raw and modeled seismic datasets.
Python 3.12+| Ingestion orchestration| Flexible API integration, JSON handling, and data processing.| Enables customizable extraction and recovery logic.
Pandas| Data manipulation| Simplifies normalization, transformation, and validation.| Converts complex API responses into tabular structures.
pandas-gbq| Warehouse loading| Provides a Python interface for loading DataFrames into BigQuery.| Simplifies warehouse integration.
Gemini 2.5 Flash| AI-assisted recovery| Analyzes runtime errors and proposes structured remediation instructions.| Reduces repetitive manual schema troubleshooting.
GitHub Actions| CI/CD and scheduling| Provides repository-based automated execution.| Removes dependency on a continuously running local machine.
dbt Cloud| Analytics engineering| Organizes transformations into reusable and testable SQL models.| Improves lineage, maintainability, and analytical consistency.
SQL| Data transformation| Enables warehouse-native transformations and analytical logic.| Reduces unnecessary data movement.
XGBoost| Machine learning| Gradient-boosted decision trees are effective for structured tabular data.| Supports classification experiments.
MLflow| Experiment tracking| Records parameters, metrics, and model artifacts.| Improves reproducibility and experiment comparison.
Streamlit| Application layer| Converts Python analytical workflows into interactive applications.| Makes analytical insights accessible to users.
Plotly| Visualization| Supports interactive charts and geographical exploration.| Improves analytical investigation.
Power BI| Executive reporting| Provides business-oriented reporting and interactive dashboards.| Communicates analytical findings to stakeholders.

---

4. End-to-End System Architecture

The architecture follows a layered data engineering approach, separating infrastructure provisioning, data ingestion, raw storage, analytical transformation, machine learning, and reporting.

High-level architecture

flowchart TD
    A["USGS Public Earthquake API"] --> B["Python Ingestion Engine"]

    B --> C["JSON Normalization & Validation"]
    C --> D["Deduplication & Incremental Filtering"]
    D --> E["BigQuery Ingestion"]

    E -->|Success| F["BigQuery Raw Dataset"]
    E -->|Failure| G["Gemini AI Recovery Agent"]

    G --> H["Structured Repair Instructions"]
    H --> I["DataFrame Validation & Repair"]
    I --> J["Controlled Retry"]
    J --> F

    K["Terraform Cloud"] --> L["GCP Infrastructure"]
    L --> F

    M["GitHub Actions"] --> B

    F --> N["dbt Staging"]
    N --> O["dbt Intermediate"]
    O --> P["Dimension Mart"]
    O --> Q["Fact Mart"]

    P --> R["Machine Learning"]
    Q --> R
    R --> S["XGBoost + MLflow"]

    P --> T["Streamlit + Plotly"]
    Q --> T
    P --> U["Power BI"]
    Q --> U

Architecture design rationale

Why a layered architecture?

Each component has a clearly defined responsibility.

- Infrastructure is separated from application logic.
- Ingestion is separated from transformation.
- Raw data is preserved independently of analytical models.
- Business logic is centralized in dbt.
- Machine learning and BI consume curated datasets rather than independently processing raw API responses.

This separation makes the platform easier to debug, extend, test, and maintain.

---

5. Infrastructure as Code — Terraform & BigQuery

5.1 Infrastructure provisioning

The platform uses HashiCorp Terraform to define and provision Google Cloud BigQuery resources.

Instead of manually creating datasets and tables through the cloud console, infrastructure definitions are maintained as version-controlled configuration files.

Why Terraform?

Manual cloud provisioning creates several operational challenges:

- Resource configurations can become inconsistent.
- Recreating environments requires repetitive manual work.
- Infrastructure changes are difficult to review.
- Deployment processes become dependent on individual operators.

Terraform addresses these problems through declarative infrastructure management.

5.2 BigQuery resource configuration

The project provisions the following resources:

Resource| Configuration| Purpose
GCP Project| "usgs-511715"| Cloud project boundary
Dataset| "Earthquake_raw"| Raw telemetry storage
Table| "raw_usgs_data"| Incoming USGS records
Location| "US"| BigQuery multi-region storage

Terraform implementation

main.tf

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

providers.tf

The provider configuration binds Terraform execution to the target GCP project using the Google provider and a version constraint of "~> 5.0".

Why BigQuery?

BigQuery provides a managed analytical warehouse without requiring the project to operate its own database infrastructure.

Its SQL processing capabilities also make it suitable for:

- Large-scale analytical queries.
- Raw and curated data separation.
- dbt-based transformations.
- Power BI connectivity.
- Machine learning feature extraction.

Important design consideration: The raw table's schema must be managed consistently with the ingestion process. Terraform provisioning alone does not guarantee automatic schema evolution or compatibility with every future API response.

---

6. Python Data Ingestion & Deduplication Engine

6.1 Data source

The platform collects seismic event data from the official USGS Earthquake API.

Data provider: United States Geological Survey

API resource:
https://earthquake.usgs.gov/fdsnws/event/1/

Response format: GeoJSON

The ingestion process uses API query parameters such as:

- "starttime"
- "endtime"
- "minmagnitude"

The current implementation targets a rolling 24-hour extraction window and a minimum magnitude threshold of 0.05.

Why GeoJSON?

GeoJSON provides a structured representation of geographical features and their associated attributes.

Each earthquake event contains two primary information groups:

Properties

- Event ID.
- Magnitude.
- Event location description.
- Event timestamp.
- Updated timestamp.
- Alert status.
- Felt reports.
- Significance score.
- Station measurements.

Geometry

- Geometry type.
- Longitude.
- Latitude.
- Depth in kilometers.

This structure allows the pipeline to retain both seismic measurements and geographical information.

6.2 Ingestion workflow

flowchart TD
    A["USGS REST API"] --> B["Fetch Recent Events"]
    B --> C["Parse GeoJSON"]
    C --> D["Normalize JSON Properties"]
    D --> E["Convert to Pandas DataFrame"]
    E --> F["Clean Columns & Nested Objects"]
    F --> G["Query Existing BigQuery Event IDs"]
    G --> H["Filter Previously Ingested Events"]
    H --> I["Validate DataFrame"]
    I --> J["Load into BigQuery"]

6.3 Data normalization

What happens?

The Python ingestion engine converts semi-structured JSON event objects into tabular DataFrame records.

Nested attributes are normalized into individual columns, while complex list structures are serialized into JSON strings where required by the warehouse loading strategy.

Why is normalization necessary?

Raw API responses are designed for flexible data exchange rather than direct analytical querying.

Normalization makes event attributes easier to:

- Validate.
- Store.
- Query.
- Transform.
- Model through dbt.

6.4 Incremental ingestion and deduplication

The ingestion process uses a rolling extraction window and checks previously stored event IDs in BigQuery.

The existing-event verification query examines records across the previous two days using the event timestamp.

The event ID ("id") acts as the logical event identifier.

Why deduplication matters

Rolling extraction windows can repeatedly return previously collected events.

Without deduplication, repeated API responses can inflate event counts, distort aggregate metrics, and introduce duplicate records into downstream analytical models.

The deduplication process reduces these risks by excluding already-ingested events.

Important: The ingestion window and deduplication logic should also account for updated USGS events. A future improvement is to use event ID plus update timestamp, or an upsert/MERGE strategy, to capture revised event attributes without creating duplicates.

---

7. AI-Powered Self-Healing Ingestion — Gemini 2.5 Flash

7.1 Problem statement

Traditional ingestion systems commonly rely on predefined schemas and deterministic data conversion rules.

When an API introduces an unexpected attribute or changes an existing data type, the ingestion process may fail because the incoming DataFrame no longer matches the destination table schema.

This project introduces an AI-assisted recovery mechanism to improve ingestion resilience.

7.2 Why Gemini 2.5 Flash?

Gemini 2.5 Flash is integrated as an error-diagnosis and remediation assistant.

It can inspect structured error context and recommend transformations based on the observed incompatibility.

Rather than manually investigating every supported schema mismatch, the recovery agent can propose a machine-readable remediation plan.

7.3 Self-healing architecture

flowchart TD
    A["Normalized Pandas DataFrame"] --> B["BigQuery Write Attempt"]
    B -->|Success| C["Ingestion Completed"]
    B -->|Failure| D["Capture Exception"]

    D --> E["Collect Error & Schema Context"]
    E --> F["Gemini 2.5 Flash"]

    F --> G["Structured JSON Repair Plan"]
    G --> H["Validate Proposed Actions"]

    H -->|Approved| I["Apply In-Memory Repair"]
    H -->|Rejected| J["Log & Quarantine Failure"]

    I --> K["Retry BigQuery Write"]
    K -->|Success| C
    K -->|Failure| J

7.4 Self-healing execution logic

The recovery process follows four stages.

Stage 1 — Failure interception

The ingestion engine catches exceptions raised during the BigQuery loading operation.

Stage 2 — Context analysis

The agent receives relevant diagnostic information:

- Error traceback.
- DataFrame column names.
- Data type information.
- Representative payload samples.
- Destination schema information, where available.

Stage 3 — Structured remediation

Gemini returns a JSON-formatted repair proposal.

Potential remediation actions include:

- Serializing nested arrays into JSON strings.
- Converting compatible values into expected data types.
- Identifying conflicting columns.
- Recommending the removal of unsupported attributes when explicitly permitted by the schema policy.

Stage 4 — Validation and retry

The ingestion engine validates the proposed changes, applies permitted transformations in memory, and retries the warehouse write.

Why this architecture is useful

- Reduces repetitive manual debugging.
- Helps diagnose previously unseen data compatibility issues.
- Keeps ingestion logic separate from AI diagnosis.
- Supports extensible recovery rules.
- Provides a foundation for intelligent data-quality automation.

Production reliability considerations

AI-generated transformations must never be treated as automatically trustworthy.

A production implementation should enforce:

1. Strict JSON schema validation.
2. Explicit allowlisted transformation operations.
3. Mandatory preservation of business-critical fields.
4. Row-count and schema checks before retry.
5. Limited retry attempts.
6. Failed-record quarantine.
7. Audit logging of every AI-proposed repair.
8. Human approval for destructive or ambiguous transformations.

Design principle: Gemini proposes a repair; deterministic application logic validates and executes only permitted actions.

The recovery mechanism improves resilience, but it does not guarantee zero downtime or successful recovery from every possible failure.

---

8. Automated Continuous Ingestion — GitHub Actions

8.1 Workflow overview

The platform uses GitHub Actions to execute the Python ingestion service automatically.

The workflow supports:

- Scheduled cron execution.
- Manual execution through "workflow_dispatch".
- Ephemeral Ubuntu-hosted runners.
- Python 3.12 environment setup.
- Dependency installation.
- Secure credential injection.
- Automated ingestion execution.

8.2 Execution architecture

flowchart TD
    A["GitHub Scheduler / Manual Trigger"] --> B["Ubuntu Hosted Runner"]
    B --> C["Checkout Repository"]
    C --> D["Configure Python 3.12"]
    D --> E["Install requirements.txt"]
    E --> F["Load GitHub Secrets"]
    F --> G["Authenticate with GCP"]
    G --> H["Execute main.py"]
    H --> I["USGS Data Ingestion"]
    I --> J["BigQuery Raw Dataset"]

8.3 Secure credential management

The workflow uses encrypted GitHub repository secrets to supply credentials at runtime.

Expected configuration:

Secret| Purpose
"GCP_SA_KEY"| Google Cloud service account credentials
"GEMINI_API_KEY"| Gemini API authentication

Why GitHub Secrets?

Hardcoding credentials inside Python files or repository configuration creates a serious security risk.

GitHub Secrets keeps sensitive values outside the source code and makes them available to the workflow when required.

8.4 Why scheduled execution?

A scheduled workflow removes the need for a continuously running local machine or manually operated ingestion script.

The current architecture is scheduled batch ingestion rather than continuous streaming.

GitHub Actions cron execution can be delayed by shared runner availability and scheduling constraints. Therefore, the configured cron interval should be treated as the intended execution frequency, not a guaranteed execution time.

Operational value

- Automated recurring data collection.
- Reproducible execution environments.
- Reduced local machine dependency.
- Centralized workflow configuration.
- Easier operational monitoring.

---

9. Analytics Engineering & Data Transformation — dbt Cloud

9.1 Why dbt?

Raw seismic telemetry is not immediately suitable for business intelligence or analytical modeling.

It contains semi-structured attributes, inconsistent data types, and geographical information that needs standardization.

dbt provides a modular SQL transformation framework that converts raw warehouse data into reusable analytical models.

Why separate staging, intermediate, and mart layers?

Each layer has a distinct responsibility:

Layer| Responsibility| Why it exists
Source| Raw API data| Preserve the original ingestion boundary
Staging| Standardization and type casting| Establish consistent field definitions
Intermediate| Complex transformations and enrichment| Centralize reusable business logic
Marts| Analytical dimensions and facts| Provide business-ready datasets

9.2 dbt project structure

USGS/
├── models/
│   └── Earthquake_usgs/
│       ├── intermediate/
│       │   └── int_earthquake_enriched.sql
│       ├── marts/
│       │   ├── dim_earthquake_location.sql
│       │   ├── fct_earthquake_events.sql
│       │   └── marts_test.yml
│       ├── earthquake.sql
│       └── earthquake.yml
├── macros/
├── seeds/
├── snapshots/
└── tests/

9.3 dbt lineage

flowchart TD
    A["BigQuery: Earthquake_raw.raw_usgs_data"]
    A --> B["earthquake.sql - Staging"]
    B --> C["int_earthquake_enriched.sql - Intermediate"]
    C --> D["dim_earthquake_location.sql"]
    C --> E["fct_earthquake_events.sql"]
    D --> F["Streamlit / Power BI / ML"]
    E --> F

9.4 Source freshness monitoring

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
          loaded_at_field: timestamp_millis(
            cast(properties_updated as int64)
          )
          freshness:
            warn_after:
              count: 5
              period: day
            error_after:
              count: 10
              period: day

Why source freshness?

A technically successful transformation does not necessarily mean the upstream data is current.

Freshness checks monitor the time elapsed since the latest source update.

The current policy is:

- Warning after five days.
- Error after ten days.

This makes delayed ingestion more visible and prevents stale data from silently appearing reliable.

Important: These thresholds monitor source update timestamps, not necessarily pipeline execution timestamps. A separate operational ingestion timestamp is recommended for measuring actual pipeline latency.

9.5 Staging model — "earthquake.sql"

The staging model standardizes raw USGS attributes into consistent analytical field names and data types.

Key transformations include:

- Event ID standardization.
- Magnitude conversion.
- Timestamp conversion.
- Alert and status normalization.
- Station metric extraction.
- Geometry attribute selection.

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

        safe_cast(properties_felt as int64) as total_felt_reports,
        safe_cast(properties_cdi as float64) as max_reported_intensity,
        safe_cast(properties_mmi as float64) as instrumental_intensity,

        cast(properties_alert as string) as alert_level,
        safe_cast(properties_tsunami as int64) as has_tsunami_risk,
        safe_cast(properties_sig as int64) as significance_score,

        cast(properties_net as string) as network_id,
        cast(properties_code as string) as network_event_code,

        safe_cast(properties_nst as int64) as total_stations_used,
        safe_cast(properties_dmin as float64) as min_station_distance,
        safe_cast(properties_rms as float64) as rms_travel_time,
        safe_cast(properties_gap as float64) as azimuthal_gap,

        cast(geometry_type as string) as geometry_type,
        geometry_coordinates as coordinates_array

    from raw_source

)

select *
from cleaned_eq

Why use safe casting?

A regular cast can fail when a source value is malformed or incompatible with the expected data type.

Safe casting returns NULL for incompatible values, allowing the transformation to continue while exposing invalid values for data-quality checks.

Missing measurements should not automatically be converted to zero. A missing magnitude is not equivalent to a magnitude of zero.

9.6 Intermediate enrichment model

File: "int_earthquake_enriched.sql"

The intermediate model centralizes geographical parsing, duplicate selection, event categorization, and analytical enrichment.

Why an intermediate layer?

Complex business logic should not be independently repeated across multiple marts.

Centralizing it improves consistency, maintainability, and downstream model reuse.

Key transformations:

Transformation| Business purpose
Longitude extraction| Geographic visualization
Latitude extraction| Geographic visualization
Depth extraction| Earthquake depth analysis
Window functions| Duplicate event handling
Magnitude classification| Event severity segmentation
Depth classification| Seismic depth analysis
Event time extraction| Temporal analysis
Risk profile flags| Analytical risk segmentation
Reporting delay| Event update timing analysis

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

        extract(hour from event_timestamp) as event_hour,

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
            when has_tsunami_risk = 1 and magnitude >= 6.0
                then 'Critical High Risk'

            when has_tsunami_risk = 1 or magnitude >= 5.0
                then 'Elevated Risk'

            else 'Standard Monitoring'
        end as risk_profile_flag

    from extracted_coordinates

    where row_num = 1

)

select *
from insights

Why window functions?

"ROW_NUMBER()" allows the transformation to select one preferred record for each earthquake ID.

The latest update timestamp is prioritized so that revised event records can be retained.

Why business flags?

Raw measurements are useful for scientific analysis, but categorical fields make reporting easier for stakeholders.

Magnitude classes, depth categories, and analytical risk profiles help users segment events without repeatedly implementing the same SQL logic.

Important: The risk profile is an analytical classification created from magnitude and the USGS tsunami flag. It is not an official USGS warning or a scientifically validated earthquake-danger prediction.

The country/state field derived from the USGS place description should also be treated as an estimated text attribute rather than authoritative reverse-geocoded geography.

9.7 Dimensional and fact marts

The final analytical layer consists of two principal tables.

Dimension: "dim_earthquake_location"

Purpose: Store geographical and descriptive event attributes.

Attribute| Purpose
earthquake_id| Event identifier
place_description| Source location description
event_title| Event display name
geometry_type| GeoJSON geometry type
longitude| Geographic longitude
latitude| Geographic latitude
depth_km| Event depth
depth_category| Depth classification
estimated_location_country_or_state| Estimated geographical description

Why a dimension table?

Separating descriptive geographical attributes from numerical event measurements makes the analytical model easier to understand and use in geographical reporting.

Fact: "fct_earthquake_events"

Purpose: Store measurable seismic event attributes and analytical classifications.

Attribute group| Example fields
Event identifiers| earthquake_id, network_id
Measurements| magnitude, significance_score
Alert information| alert_level, risk_profile_flag
Station information| total_stations_used, azimuthal_gap
Intensity information| max_reported_intensity, instrumental_intensity
Temporal attributes| event_timestamp, event_hour, event_month_name
Operational attributes| updated_timestamp, pipeline_reporting_delay_minutes

Why a fact table?

The fact model creates a consistent analytical source for aggregations, trends, comparisons, and reporting KPIs.

9.8 Automated data-quality testing

File: "marts_test.yml"

The project implements dbt tests to validate important analytical constraints.

Test| Purpose
Unique| Prevent duplicate event identifiers
Not Null| Ensure required attributes are populated
Accepted Values| Validate predefined classifications
Relationships| Verify fact-to-dimension referential integrity

Example:

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

A dashboard can look correct while silently displaying duplicated or incomplete records.

Automated tests establish measurable quality requirements before data is consumed by downstream applications.

Additional production-quality tests should cover coordinate ranges, valid magnitude ranges, missing timestamps, and null geographical values.

9.9 dbt Cloud orchestration

Operational property| Project configuration
Job name| "usgs_analytic_pipeline"
Platform| dbt Cloud
Environment| "usgs"
Recorded completed runs| 84
Reported successful runs| 100%
Reported average execution| Under one minute

Why dbt Cloud scheduling?

Automated transformation jobs reduce the need for manual SQL execution and help maintain a consistent analytical layer.

The recorded run metrics provide an operational reference for the executions observed during the project's reporting period.

---

10. Machine Learning — XGBoost & MLflow

10.1 Objective

The project extends analytical reporting with a supervised machine learning classification experiment.

The ML workflow extracts structured seismic attributes from the BigQuery analytical marts, prepares a modeling dataset, trains an XGBoost classifier, and records experiment metadata through MLflow.

Why XGBoost?

XGBoost uses gradient-boosted decision trees and is particularly useful for structured tabular datasets.

It supports:

- Nonlinear relationships.
- Feature interactions.
- Efficient model training.
- Regularization.
- Configurable classification objectives.

10.2 ML architecture

flowchart TD
    A["BigQuery Analytical Marts"] --> B["Python Data Extraction"]
    B --> C["Feature Engineering"]
    C --> D["Data Cleaning"]
    D --> E["Stratified Train/Test Split"]
    E --> F["Feature Scaling"]
    F --> G["XGBoost Classifier"]
    G --> H["Model Evaluation"]
    H --> I["MLflow Tracking"]

    I --> J["Parameters"]
    I --> K["Metrics"]
    I --> L["Model Artifacts"]

10.3 Dataset preparation

The modeling workflow uses the following analytical attributes:

- Depth.
- Latitude.
- Longitude.
- Magnitude.
- Event hour.
- Total seismic stations.
- Azimuthal gap.
- Additional selected event attributes.

The current experiment defines a binary classification target:

is_high_risk = (df["magnitude"] >= 4.0).astype(int)

This creates two categories:

Target| Classification
0| Magnitude below 4.0
1| Magnitude equal to or above 4.0

Important modeling limitation:

Magnitude is also listed among the original input features. Because the target is directly derived from magnitude, including magnitude in the model features causes target leakage.

A model can simply learn the threshold rule rather than discover an independent predictive relationship.

Therefore, the original reported ROC-AUC of 1.0000 and classification metrics of 1.00 must be treated as results from the initial experiment, not evidence of genuine predictive capability.

10.4 Recommended model validation

For a meaningful classification experiment:

1. Remove magnitude from the input features when predicting a magnitude-defined target.
2. Use chronological train/test splitting when evaluating performance on future events.
3. Compare against simple baseline classifiers.
4. Evaluate precision, recall, F1-score, ROC-AUC, and PR-AUC.
5. Investigate class imbalance.
6. Record all experiment configurations in MLflow.
7. Evaluate whether the chosen features provide useful information beyond the target definition.

A further improvement is to define a scientifically meaningful future outcome and use historical information only to predict that outcome.

Scope clarification: This project currently demonstrates threshold-based seismic event classification, not earthquake occurrence forecasting, earthquake timing prediction, or an operational early-warning system.

10.5 Initial experiment configuration

Parameter| Initial value
Algorithm| XGBoost Classifier
n_estimators| 150
max_depth| 6
learning_rate| 0.05
Training split| 80%
Testing split| 20%
Split strategy| Stratified
Dataset records| 32,675
Initial feature count| 8
Experiment tracking| MLflow
Tracking backend| SQLite

10.6 MLflow experiment tracking

MLflow records experiment parameters, evaluation metrics, and model artifacts.

Why MLflow?

Machine learning experiments involve repeated model configurations and evaluation cycles.

Without systematic tracking, comparing model performance and reproducing earlier experiments becomes difficult.

MLflow helps maintain:

- Experiment history.
- Hyperparameter records.
- Evaluation metrics.
- Model artifacts.
- Reproducibility.

The tracking interface also provides a foundation for future model comparison and model registry integration.

---

11. Interactive Analytics Application — Streamlit & Plotly

11.1 Application overview

The platform includes an interactive web application developed using Streamlit and Plotly.

The application queries the curated BigQuery dimension and fact marts to provide a geographical and analytical view of global seismic activity.

Application technology:

- Streamlit.
- Python.
- Plotly.
- Google BigQuery.
- Streamlit Secrets.
- Streamlit Community Cloud.

11.2 Application architecture

flowchart TD
    A["Streamlit Community Cloud"] --> B["Secure BigQuery Authentication"]
    B --> C["Read Analytical Marts"]
    C --> D["Cached Data Layer"]
    D --> E["Interactive Sidebar Filters"]

    E --> F["KPI Cards"]
    E --> G["Global Earthquake Map"]
    E --> H["Plotly Analytics"]
    E --> I["Event Data Tables"]

11.3 Secure authentication and caching

The application uses Streamlit Secrets to store Google Cloud service account credentials.

Example configuration reference:

st.secrets["GCP_SA_KEY"]

Data retrieval uses Streamlit caching:

@st.cache_data(ttl=3600)

Why caching?

Repeatedly querying the same analytical tables can increase warehouse consumption and application response times.

Caching stores previously retrieved results temporarily, reducing unnecessary query execution and improving the user experience.

The current cache lifetime is one hour.

11.4 Interactive features

Feature| Implementation| User value
Magnitude filtering| Interactive slider| Isolate selected event intensities
Alert filtering| Multi-select controls| Investigate alert categories
KPI monitoring| Streamlit metrics| Summarize seismic activity
Global map| Latitude/longitude plotting| Explore geographical distribution
Location ranking| Top 10 location table| Identify frequently reported areas
Event breakdown| Plotly donut chart| Compare event categories
Alert distribution| Plotly charts| Explore alert classifications
Hourly trends| Time-based charts| Identify activity patterns
Monthly trends| Temporal visualizations| Explore historical distributions

11.5 KPI monitoring

The application presents:

- Total seismic events.
- Maximum magnitude.
- Average magnitude.
- Maximum depth.
- Average depth.

Why KPI cards?

KPI cards provide an immediate overview of the selected dataset without requiring users to interpret multiple detailed charts.

11.6 Geospatial analysis

The interactive map uses event coordinates to visualize geographical seismic activity.

The application also provides a Top 10 location table based on event frequency.

Example geographical areas include:

- Fiji region.
- South Sandwich Islands.
- Kermadec Islands.

Why geographical visualization?

Earthquake data has an inherently spatial dimension.

A geographical view helps users understand where events are concentrated and how seismic activity is distributed across different regions.

11.7 Interactive Plotly analytics

The application includes:

Event Type Distribution

A donut chart comparing event types, including earthquakes and other event categories reported by USGS.

Alert Level Distribution

A visual breakdown of available alert categories such as green, yellow, orange, and red.

Hourly Activity

Line or bar charts showing event frequency across hours.

Monthly Activity

Charts showing event counts across monthly periods.

These visualizations support interactive investigation and make analytical patterns easier to communicate.

---

12. Executive Business Intelligence — Power BI

12.1 Reporting objective

The project includes an executive-oriented Power BI dashboard connected to the BigQuery analytical marts.

The report translates structured seismic data into business-friendly KPIs, geographical summaries, temporal trends, and analytical risk classifications.

Why Power BI?

While SQL and Python are powerful analytical tools, executive stakeholders often require a visual reporting interface that allows them to explore metrics without writing queries.

Power BI provides:

- Interactive filtering.
- KPI monitoring.
- Dimensional analysis.
- Geographical visualization.
- Executive reporting.
- Shareable analytical reports.

12.2 Power BI data architecture

flowchart TD
    A["BigQuery: dim_earthquake_location"] --> C["Power BI Data Model"]
    B["BigQuery: fct_earthquake_events"] --> C

    C --> D["Relationship on earthquake_id"]
    D --> E["Executive Dashboard"]

    E --> F["KPI Cards"]
    E --> G["Monthly Trends"]
    E --> H["Global Location Map"]
    E --> I["Risk & Alert Matrix"]

12.3 Dashboard components

A. Executive KPI cards

The dashboard displays:

- Total earthquake events.
- Average magnitude.
- Average depth.
- Average azimuthal gap.

Why these metrics?

They provide an immediate summary of the selected event population and its key seismic characteristics.

B. Temporal trend analysis

A monthly earthquake volume chart presents event frequency across calendar months.

Why this matters:

Temporal analysis helps stakeholders compare event distributions over time.

For meaningful seasonal analysis, the reporting model should retain year and month together, rather than aggregating all January records across different years into a single category.

C. Geographical distribution

The geographical reporting layer combines:

- Latitude.
- Longitude.
- Location descriptions.
- Estimated country/state attributes.

Why geographical analysis?

It provides a visual overview of event distribution and allows users to examine locations with higher reported activity.

D. Risk and alert matrix

The dashboard includes analytical classifications such as:

- Critical High Risk.
- Elevated Risk.
- Standard Monitoring.
- Available USGS alert categories.
- Significance scores.

Why this matters:

A structured matrix makes it easier to compare event characteristics and prioritize analytical investigation.

These project-defined categories should not be interpreted as official emergency response instructions.

12.4 Executive reporting value

Power BI serves as the final business intelligence layer, translating warehouse-level analytical models into accessible reporting for stakeholders.

It bridges the gap between technical data processing and business-oriented decision-making.

---

13. Data Quality, Reliability & Operational Considerations

Reliability is addressed at multiple stages of the platform rather than being treated as a single transformation-level responsibility.

Layer| Validation mechanism| Why it matters
API ingestion| Payload normalization| Standardizes incoming data
Python processing| Data type and column checks| Detects malformed records
Deduplication| Existing event ID checks| Prevents duplicate ingestion
AI recovery| Structured repair validation| Controls automated corrections
BigQuery| Warehouse schema compatibility| Maintains storage consistency
dbt source| Freshness monitoring| Detects stale source data
dbt models| Type standardization| Improves analytical consistency
dbt tests| Unique, not null, accepted values, relationships| Validates business rules
ML workflow| Train/test validation| Evaluates model behavior
Dashboard| Filter and query logic| Supports consistent reporting

Reliability improvements to consider

The next engineering iteration can introduce:

- Explicit source schema contracts.
- Failed-record quarantine tables.
- Ingestion audit metadata.
- Retry limits and exponential backoff.
- Pipeline execution timestamps.
- Event update handling through BigQuery MERGE.
- Automated alerting for failed ingestion.
- Data-quality monitoring across transformation layers.

Why operational metadata?

Without execution metadata, it is difficult to distinguish an event's original occurrence time, its latest source update time, and the time the platform actually ingested it.

Separating these timestamps provides more accurate operational monitoring and latency analysis.

---

14. Security & Credential Management

Security is incorporated into the deployment and application architecture.

Component| Security approach
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
- Review AI-generated transformations before execution.
- Protect Terraform state and its access credentials.

These controls establish a foundation for secure cloud deployment and operational maintenance.

---

15. Repository Structure

The repository separates infrastructure, ingestion, orchestration, analytical transformations, machine learning, and application reporting.

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
│       │
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
"main.py"| USGS API ingestion, normalization, deduplication, Gemini-assisted recovery
"main.tf"| BigQuery infrastructure provisioning
"providers.tf"| Terraform Google Cloud provider configuration
"usgs_ingestion.yml"| Scheduled GitHub Actions execution
"earthquake.sql"| dbt staging transformation
"int_earthquake_enriched.sql"| Analytical enrichment and business logic
"dim_earthquake_location.sql"| Geographical dimension
"fct_earthquake_events.sql"| Seismic event fact table
"marts_test.yml"| dbt data-quality tests
"train_model.py"| XGBoost training and MLflow tracking
"usgs_python_dashboard.py"| Interactive Streamlit application
"requirements.txt"| Python dependencies
"dbt_project.yml"| dbt project configuration

---

16. Deployment & Setup Guide

The following guide describes the main deployment sequence. Exact commands and configuration values should match the current repository implementation.

Prerequisites

- Python 3.12 or later.
- Google Cloud account.
- BigQuery enabled.
- Google Cloud service account.
- Terraform CLI and HCP Terraform Cloud configuration, if used.
- Gemini API key.
- GitHub repository.
- dbt Cloud account.
- Streamlit Community Cloud account.
- Power BI Desktop.

Step 1 — Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>

cd USGS-REALTIME-EARTHQUAKE-DATA-PIPELINE

Step 2 — Configure Python

python -m venv venv

Activate the environment:

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Step 3 — Configure cloud credentials

Configure Google Cloud authentication using a service account with the minimum required permissions.

Set the required environment variables:

GCP_SA_KEY
GEMINI_API_KEY

Do not commit actual credentials or ".env" files to GitHub.

Step 4 — Provision infrastructure

Initialize Terraform:

terraform init

Validate configuration:

terraform validate

Review the proposed changes:

terraform plan

Apply the reviewed infrastructure configuration:

terraform apply

Step 5 — Execute ingestion

python main.py

Verify that records are successfully loaded into:

Earthquake_raw.raw_usgs_data

Step 6 — Configure dbt

Configure the BigQuery connection in the dbt Cloud environment.

Execute the transformation and validation workflow using the configured project and job.

Typical dbt commands:

dbt debug
dbt source freshness
dbt run
dbt test

Step 7 — Train the ML model

python ML/train_model.py

Verify the experiment parameters, metrics, and model artifacts in MLflow.

Step 8 — Launch the Streamlit application

streamlit run usgs_python_dashboard.py

Configure Streamlit Cloud deployment using the repository and the required secrets.

Step 9 — Configure Power BI

Connect Power BI to the BigQuery analytical marts.

Configure the relationship between the dimension and fact tables using "earthquake_id", then validate the report's filters, measures, and visualizations.

---

17. Project Performance & Recorded Metrics

The following metrics describe the project's reported implementation and execution history.

Metric| Recorded value
Historical dataset records used in ML| 32,675
Initial ML feature attributes| 8
XGBoost estimators| 150
dbt completed job runs| 84
Reported dbt success rate| 100%
Reported average dbt build duration| Under 1 minute
Source freshness warning threshold| 5 days
Source freshness error threshold| 10 days
Application cache lifetime| 1 hour

ML evaluation note: The initial reported ROC-AUC and classification metrics of 1.00 are not presented as validated predictive performance because the original experiment contains target leakage. A leakage-free evaluation is required before publishing corrected performance metrics.

These measurements are project-reported results, not independently audited production SLAs.

---

18. Engineering Challenges & Solutions

Engineering challenge| Implemented approach| Why it matters
Semi-structured GeoJSON| Pandas normalization| Converts API payloads into usable records
Nested geographical arrays| JSON serialization and coordinate extraction| Supports storage and spatial analysis
Duplicate API responses| BigQuery event ID verification| Protects aggregate accuracy
Schema incompatibilities| Gemini-assisted diagnosis and repair| Reduces manual debugging
Inconsistent analytical fields| dbt staging models| Establishes standardized definitions
Complex business logic| Intermediate SQL models| Avoids duplicated transformations
Data integrity| dbt automated tests| Detects analytical inconsistencies
Repeated warehouse queries| Streamlit caching| Reduces unnecessary data retrieval
Experiment reproducibility| MLflow| Maintains model experiment history
Executive data consumption| Power BI| Makes analytics accessible to stakeholders

---

19. Limitations & Future Engineering Roadmap

The current architecture provides a foundation for further development. Several improvements can extend its scalability, reliability, and analytical capabilities.

Area| Future enhancement| Expected benefit
Streaming ingestion| Google Pub/Sub + Dataflow| Lower-latency event processing
Cloud execution| Cloud Run| Managed ingestion execution
Orchestration| Cloud Composer / Airflow| Advanced dependency management
Data modeling| Incremental dbt models| More efficient processing as data grows
Schema management| Versioned schema contracts| Safer schema evolution
AI recovery| Validated repair policies and audit history| More controlled automation
Data quality| Great Expectations or additional dbt tests| Broader validation coverage
Machine learning| Leakage-free temporal evaluation| More meaningful model assessment
ML operations| MLflow Model Registry| Centralized model lifecycle management
Monitoring| Cloud Logging and alerting| Improved operational visibility
Infrastructure| Terraform modules and remote state controls| Better infrastructure governance
Data storage| Partitioning and clustering| More efficient warehouse queries

Long-term architectural direction

The future architecture can evolve from scheduled batch ingestion into an event-driven data processing platform.

A possible extension:

flowchart TD
    A["USGS Event API"] --> B["Cloud Run Ingestion Service"]
    B --> C["Google Pub/Sub"]
    C --> D["Dataflow Processing"]
    D --> E["BigQuery Raw Layer"]
    E --> F["dbt Transformation"]
    F --> G["Analytical Marts"]
    G --> H["MLflow + ML Models"]
    G --> I["Streamlit"]
    G --> J["Power BI"]
    K["Cloud Monitoring"] --> B
    K --> C
    K --> D

Why evolve toward event-driven processing?

Scheduled batch processing is appropriate for periodic data extraction, but event-driven architecture can reduce processing latency and improve responsiveness when incoming events need to be processed more frequently.

This is a future architectural direction, not a description of the current GitHub Actions implementation.

---

20. Business & Analytical Impact

The platform is designed to convert publicly available seismic telemetry into structured and accessible analytical information.

Its value is not limited to collecting earthquake records.

It provides a complete workflow for:

- Centralizing seismic event information.
- Standardizing geographical and numerical attributes.
- Improving ingestion resilience.
- Monitoring source freshness and data integrity.
- Segmenting events using analytical classifications.
- Exploring geographical activity patterns.
- Tracking machine learning experiments.
- Communicating findings through interactive reports.

Stakeholder value

Stakeholder| Potential value
Data Engineers| Automated ingestion and cloud infrastructure
Analytics Engineers| Modular dbt transformations and tested marts
Data Analysts| Query-ready seismic datasets
Researchers| Geographical and temporal event exploration
Business stakeholders| Executive KPIs and analytical reporting
ML practitioners| Structured feature datasets and experiment tracking

Important: This is an analytical monitoring and research platform. It does not replace official earthquake early-warning systems, geological hazard assessments, or emergency response authorities.

---

21. Data Source & References

Primary data provider: United States Geological Survey (USGS)

- USGS Earthquake Hazards Program: https://earthquake.usgs.gov/
- USGS FDSN Event Web Service: https://earthquake.usgs.gov/fdsnws/event/1/
- USGS Earthquake GeoJSON Feed: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

Technology documentation:

- Google BigQuery: https://cloud.google.com/bigquery/docs
- Terraform Google Provider: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Gemini API: https://ai.google.dev/gemini-api/docs
- dbt Documentation: https://docs.getdbt.com/
- GitHub Actions: https://docs.github.com/actions
- XGBoost: https://xgboost.readthedocs.io/
- MLflow: https://mlflow.org/docs/latest/
- Streamlit: https://docs.streamlit.io/
- Plotly: https://plotly.com/python/
- Power BI: https://learn.microsoft.com/power-bi/

---

22. Project Links & Visual Demonstration

Resource| Link
GitHub Repository| "Add repository URL" (YOUR_GITHUB_REPOSITORY_URL)
Live Streamlit Application| "Add deployed application URL" (YOUR_STREAMLIT_APP_URL)
Power BI Report| "Add published report URL, if available" (YOUR_POWER_BI_REPORT_URL)
Architecture Diagram| "Add diagram URL, if available" (YOUR_ARCHITECTURE_DIAGRAM_URL)

Application screenshots

Add actual screenshots from the deployed application and reporting environment.

Streamlit — Global Seismic Monitoring

"![Streamlit Dashboard](docs/images/streamlit_dashboard.png)"

Power BI — Executive Analytics

"![Power BI Dashboard](docs/images/powerbi_dashboard.png)"

MLflow — Experiment Tracking

"![MLflow Experiments](docs/images/mlflow_experiments.png)"

Note: Replace these references with real screenshots and ensure the image files exist in the repository.

---

23. Conclusion

The USGS Global Seismic Intelligence Platform demonstrates an integrated approach to modern cloud-native data engineering and analytics.

By combining Terraform-based infrastructure provisioning, Python ingestion, Gemini-assisted recovery, BigQuery warehousing, dbt analytics engineering, XGBoost experimentation, MLflow tracking, Streamlit application development, and Power BI reporting, the project establishes a complete data lifecycle from source extraction to decision-oriented analytics.

The architecture emphasizes modularity, automation, data quality, maintainability, and responsible AI integration.

More importantly, it demonstrates how independent technologies can work together to solve a practical data processing and analytical problem.

The ultimate objective is to transform raw global seismic telemetry into reliable, structured, and accessible intelligence.

---

Author & Project Ownership

Developed as an independent end-to-end data engineering and analytics project.

Technologies: Python | SQL | Terraform | Google Cloud | BigQuery | Gemini AI | dbt | GitHub Actions | XGBoost | MLflow | Streamlit | Plotly | Power BI

Built to explore the intersection of Data Engineering, Analytics Engineering, AI-assisted automation, Machine Learning, and Business Intelligence.
