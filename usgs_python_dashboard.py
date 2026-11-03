import json
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration (Must be the first Streamlit command)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="USGS Earthquake Risk Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Custom CSS Styling (Dark Mode SOC Theme)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { font-size: 22px; color: #00FFAA; }
    
    /* Modern KPI Cards */
    .kpi-box {
        background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    }
    .kpi-title {
        color: #8B949E;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #58A6FF;
        font-size: 19px;
        font-weight: 700;
        word-wrap: break-word;
    }
    h1, h2, h3 { color: #58A6FF; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. Secure Credentials & BigQuery Client Setup
# -----------------------------------------------------------------------------
@st.cache_resource
def init_bigquery_client():
    try:
        # Securely loading credentials from Streamlit Secrets Management
        if "GCP_SA_KEY" in st.secrets:
            service_account_info = dict(st.secrets["GCP_SA_KEY"])
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            client = bigquery.Client(
                credentials=credentials, project=service_account_info.get("project_id")
            )
            return client
        else:
            st.error("🚨 GCP_SA_KEY not found in Streamlit secrets! Please configure it in your deployment settings.")
            st.stop()
    except Exception as e:
        st.error(f"❌ Failed to initialize BigQuery client: {e}")
        st.stop()

bq_client = init_bigquery_client()

# -----------------------------------------------------------------------------
# 4. Cached Data Ingestion from BigQuery Data Marts
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data_from_bigquery():
    try:
        query_loc = "select * from `usgs-511715.raw_usgs_data_marts.dim_earthquake_location`"
        dim_locations = bq_client.query(query_loc).to_dataframe()

        query_events = "select * from `usgs-511715.raw_usgs_data_marts.fct_earthquake_events`"
        fct_events = bq_client.query(query_events).to_dataframe()

        return dim_locations, fct_events
    except Exception as e:
        st.error(f"❌ Error fetching data from BigQuery tables: {e}")
        return pd.DataFrame(), pd.DataFrame()

dim_locations, fct_events = load_data_from_bigquery()

# Validate loaded data frames
if dim_locations.empty or fct_events.empty:
    st.warning("⚠️ No data retrieved from BigQuery marts. Please verify your table schemas and data pipelines.")
    st.stop()

# Safe Data Join on earthquake_id
df = pd.merge(fct_events, dim_locations, on="earthquake_id", how="inner")

# -----------------------------------------------------------------------------
# 5. SIDEBAR FILTERS & CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Dashboard Data")

# Magnitude Filter Slider
if "magnitude" in df.columns and not df["magnitude"].empty:
    min_mag = float(df["magnitude"].min())
    max_mag = float(df["magnitude"].max())
    selected_mag_range = st.sidebar.slider(
        "Select Magnitude Range",
        min_value=min_mag,
        max_value=max_mag,
        value=(min_mag, max_mag),
    )
else:
    selected_mag_range = (0.0, 10.0)

# Alert Level Multi-select Filter
if "alert_level" in df.columns:
    all_alerts = df["alert_level"].dropna().unique().tolist()
    selected_alerts = st.sidebar.multiselect(
        "Select Alert Levels", options=all_alerts, default=all_alerts
    )
else:
    selected_alerts = []

# Apply Filters to DataFrame
df_filtered = df[
    (df["magnitude"] >= selected_mag_range[0]) &
    (df["magnitude"] <= selected_mag_range[1])
]

if "alert_level" in df.columns and selected_alerts:
    df_filtered = df_filtered[df_filtered["alert_level"].isin(selected_alerts)]

# -----------------------------------------------------------------------------
# 6. MAIN DASHBOARD CONTENT & KPIS
# -----------------------------------------------------------------------------
st.title("⚡ USGS Real-Time Earthquake Analytics Platform")
st.caption(
    "Developer: Muhammad Anas | GitHub: [mr-Anas-tech](https://github.com/mr-Anas-tech) | "
    f"Showing **{len(df_filtered):,}** of **{len(df):,}** seismic events"
)

st.subheader("📊 Real-Time Earthquake Overview")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Events", f"{len(df_filtered):,}")

with col2:
    max_mag = round(df_filtered["magnitude"].max(), 2) if "magnitude" in df_filtered.columns and not df_filtered.empty else 0
    st.metric(label="Maximum Magnitude", value=max_mag)

with col3:
    avg_mag = round(df_filtered["magnitude"].mean(), 2) if "magnitude" in df_filtered.columns and not df_filtered.empty else 0
    st.metric(label="Average Magnitude", value=avg_mag)

with col4:
    max_depth = round(df_filtered["depth_km"].max(), 2) if "depth_km" in df_filtered.columns and not df_filtered.empty else 0
    st.metric(label="Maximum Depth (km)", value=max_depth)

with col5:
    avg_depth = round(df_filtered["depth_km"].mean(), 2) if "depth_km" in df_filtered.columns and not df_filtered.empty else 0
    st.metric(label="Average Depth (km)", value=avg_depth)

st.divider()

# -----------------------------------------------------------------------------
# 7. MAP & TOP LOCATIONS
# -----------------------------------------------------------------------------
col_map, col_table = st.columns([1.2, 1])

with col_map:
    st.subheader("🌍 Geographic Distribution")
    if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
        st.map(df_filtered[["latitude", "longitude"]], use_container_width=True)
    else:
        st.info("Latitude/Longitude coordinates not available.")

with col_table:
    st.subheader("📍 Top 10 Locations")
    if "place_description" in df_filtered.columns and "event_type" in df_filtered.columns:
        top_locations = (
            df_filtered[["place_description", "event_type"]]
            .value_counts()
            .reset_index(name="count")
            .head(10)
        )
        st.dataframe(top_locations, use_container_width=True, hide_index=True)

st.divider()

# -----------------------------------------------------------------------------
# 8. PLOTLY CHARTS & TRENDS
# -----------------------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("🥧 Event Type Proportion")
    if "event_type" in df_filtered.columns and not df_filtered.empty:
        event_type_counts = df_filtered["event_type"].value_counts().reset_index()
        event_type_counts.columns = ["event_type", "count"]
        fig_event_type = px.pie(
            event_type_counts,
            values="count",
            names="event_type",
            template="plotly_dark",
            hole=0.4,
        )
        st.plotly_chart(fig_event_type, use_container_width=True)

with col_chart2:
    st.subheader("🚨 Alert Level Distribution")
    if "alert_level" in df_filtered.columns and not df_filtered.empty:
        alert_count = df_filtered["alert_level"].value_counts().reset_index()
        alert_count.columns = ["alert_level", "count"]
        color_map = {
            "green": "#2ecc71",
            "yellow": "#f1c40f",
            "orange": "#e67e22",
            "red": "#e74c3c",
            "None": "#95a5a6",
        }
        fig_alert = px.pie(
            alert_count,
            values="count",
            names="alert_level",
            template="plotly_dark",
            hole=0.4,
            color="alert_level",
            color_discrete_map=color_map,
        )
        st.plotly_chart(fig_alert, use_container_width=True)

# Trend Charts
col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    st.subheader("📈 Hourly Earthquake Rate")
    if "event_hour" in df_filtered.columns and not df_filtered.empty:
        hourly_events = df_filtered["event_hour"].value_counts().reset_index(name="count")
        hourly_events.columns = ["event_hour", "count"]
        hourly_events = hourly_events.sort_values(by="event_hour")
        fig_hourly = px.line(
            hourly_events,
            x="event_hour",
            y="count",
            template="plotly_dark",
            markers=True,
        )
        st.plotly_chart(fig_hourly, use_container_width=True)

with col_trend2:
    st.subheader("📅 Monthly Earthquake Trend")
    if "event_month_name" in df_filtered.columns and not df_filtered.empty:
        monthly_events = df_filtered["event_month_name"].value_counts().reset_index(name="count")
        monthly_events.columns = ["event_month_name", "count"]
        fig_monthly = px.bar(
            monthly_events,
            x="event_month_name",
            y="count",
            template="plotly_dark",
            color="count",
            color_continuous_scale="sunset",
        )
        st.plotly_chart(fig_monthly, use_container_width=True)