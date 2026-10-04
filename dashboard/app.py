from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"



from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
STORES_PATH = ROOT / "data" / "stores" / "stores.csv"

st.set_page_config(
    page_title="GeoPulse Analytics",
    page_icon="📍",
    layout="wide"
)


@st.cache_data
def read_csv(path):
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    return df


def load_gps():
    cleaned = read_csv(PROCESSED / "gps_pings_clean.csv")

    if not cleaned.empty:
        return cleaned

    # Fall back to raw GPS data if Day 12 output is missing.
    return read_csv(RAW / "gps_pings.csv")


gps = load_gps()
stores = read_csv(STORES_PATH)
zones = read_csv(RAW / "zones.csv")
zone_summary = read_csv(
    PROCESSED / "pyspark_zone_footfall.csv"
)
hourly = read_csv(
    PROCESSED / "hourly_gps_summary.csv"
)

st.title("📍 GeoPulse — Retail Mobility Analytics")
st.caption(
    "Explore simulated GPS activity, store locations, "
    "zone footfall and hourly patterns."
)

if gps.empty:
    st.error(
        "GPS data not found. Check data/raw/gps_pings.csv "
        "and data/processed/gps_pings_clean.csv."
    )
    st.stop()

# Normalize important GPS columns
if "event_timestamp" not in gps.columns and "timestamp" in gps.columns:
    gps = gps.rename(columns={"timestamp": "event_timestamp"})

required = {"latitude", "longitude", "event_timestamp"}
if not required.issubset(gps.columns):
    st.error(f"GPS data must contain: {sorted(required)}")
    st.stop()

gps["latitude"] = pd.to_numeric(gps["latitude"], errors="coerce")
gps["longitude"] = pd.to_numeric(gps["longitude"], errors="coerce")
gps["event_timestamp"] = pd.to_datetime(
    gps["event_timestamp"], errors="coerce"
)

gps = gps.dropna(
    subset=["latitude", "longitude", "event_timestamp"]
).copy()

gps = gps[
    gps["latitude"].between(-90, 90)
    & gps["longitude"].between(-180, 180)
].copy()

gps["event_date"] = gps["event_timestamp"].dt.date
gps["event_hour"] = gps["event_timestamp"].dt.hour

if gps.empty:
    st.error("No valid GPS records are available.")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

min_date = gps["event_date"].min()
max_date = gps["event_date"].max()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered = gps.copy()

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered = filtered[
        filtered["event_date"].between(start_date, end_date)
    ]

if not stores.empty and "area" in stores.columns:
    areas = sorted(stores["area"].dropna().astype(str).unique())
    selected_areas = st.sidebar.multiselect(
        "Store areas (map filter)",
        areas,
        default=areas
    )
    visible_stores = stores[
        stores["area"].astype(str).isin(selected_areas)
    ].copy()
else:
    visible_stores = stores.copy()

unique_devices = (
    filtered["device_id"].nunique()
    if "device_id" in filtered.columns
    else 0
)

# KPI cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("GPS Pings", f"{len(filtered):,}")
c2.metric("Unique Devices", f"{unique_devices:,}")
c3.metric("Stores", f"{len(visible_stores):,}")
c4.metric("Zones", f"{len(zones):,}")

st.divider()

# Map
st.subheader("GPS Activity and Store Locations")

gps_map = filtered
if len(gps_map) > 3000:
    gps_map = gps_map.sample(n=3000, random_state=42)

layers = []

if not gps_map.empty:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=gps_map,
            get_position="[longitude, latitude]",
            get_radius=45,
            get_fill_color=[30, 120, 220, 100],
            pickable=True,
            auto_highlight=True
        )
    )

if (
    not visible_stores.empty
    and {"latitude", "longitude"}.issubset(visible_stores.columns)
):
    visible_stores["latitude"] = pd.to_numeric(
        visible_stores["latitude"], errors="coerce"
    )
    visible_stores["longitude"] = pd.to_numeric(
        visible_stores["longitude"], errors="coerce"
    )
    visible_stores = visible_stores.dropna(
        subset=["latitude", "longitude"]
    )

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=visible_stores,
            get_position="[longitude, latitude]",
            get_radius=140,
            get_fill_color=[220, 50, 50, 220],
            pickable=True
        )
    )

if not filtered.empty:
    center_lat = float(filtered["latitude"].median())
    center_lon = float(filtered["longitude"].median())

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=10,
                pitch=0
            ),
            tooltip={
                "text": "{device_id}\n{store_name}\n{area}"
            },
            map_style=None
        ),
        use_container_width=True
    )

st.caption(
    "Blue points = sampled GPS pings; red points = stores. "
    "The store-area filter affects store markers, not GPS records."
)

# Hourly activity
st.subheader("Hourly GPS Activity")

hour_data = filtered.groupby(
    "event_hour", as_index=False
).size().rename(columns={"size": "total_gps_pings"})

if not hour_data.empty:
    fig = px.bar(
        hour_data,
        x="event_hour",
        y="total_gps_pings",
        labels={
            "event_hour": "Hour of day",
            "total_gps_pings": "GPS pings"
        },
        title="GPS pings by hour"
    )
    st.plotly_chart(fig, use_container_width=True)

# Zone footfall
st.subheader("Zone Footfall")

if not zone_summary.empty and {
    "zone_name", "total_gps_pings"
}.issubset(zone_summary.columns):
    zone_summary["total_gps_pings"] = pd.to_numeric(
        zone_summary["total_gps_pings"], errors="coerce"
    ).fillna(0)

    zone_fig = px.bar(
        zone_summary.sort_values(
            "total_gps_pings", ascending=False
        ),
        x="zone_name",
        y="total_gps_pings",
        labels={
            "zone_name": "Zone",
            "total_gps_pings": "GPS pings"
        },
        title="GPS activity by zone"
    )
    st.plotly_chart(zone_fig, use_container_width=True)
    st.dataframe(zone_summary, use_container_width=True)
else:
    st.info(
        "Zone summary is not available yet. Run Day 12 processing "
        "to generate pyspark_zone_footfall.csv."
    )

# Download filtered data
st.subheader("Export")

st.download_button(
    "Download filtered GPS data",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="geopulse_filtered_gps.csv",
    mime="text/csv"
)

st.caption(
    "Project note: GPS pings indicate recorded device activity, "
    "not confirmed store visits or actual customer identities."
)

st.header("📊 Day 16 Final Analytics")

summary_file = PROCESSED_DIR / "day16_project_summary.csv"

if summary_file.exists():

    final_summary = pd.read_csv(summary_file)

    st.subheader("Project Summary")

    for _, row in final_summary.iterrows():
        st.write(
            f"**{row['metric']} :** {row['value']}"
        )


peak_file = PROCESSED_DIR / "day16_peak_hour.csv"

if peak_file.exists():

    peak = pd.read_csv(peak_file)

    st.subheader("🔥 Peak Hour")

    st.dataframe(
        peak,
        use_container_width=True
    )


zone_file = PROCESSED_DIR / "day16_zone_ranking.csv"

if zone_file.exists():

    zones_final = pd.read_csv(zone_file)

    st.subheader("🏆 Zone Ranking")

    st.dataframe(
        zones_final,
        use_container_width=True
    )