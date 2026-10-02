
from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

# -------------------------------
# 1. Page setup and file paths
# -------------------------------
st.set_page_config(
    page_title="GeoPulse | Retail Mobility Analytics",
    page_icon="📍",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
STORES_FILE = ROOT / "data" / "stores" / "stores.csv"
GPS_FILE = RAW / "gps_pings.csv"
ZONES_FILE = RAW / "zones.csv"


def load_csv(path):
    """Load a CSV if it exists; otherwise return an empty DataFrame."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


# -------------------------------
# 2. Load and clean data
# -------------------------------
gps = load_csv(GPS_FILE)
stores = load_csv(STORES_FILE)
zones = load_csv(ZONES_FILE)

if gps.empty:
    st.error(f"GPS data not found or empty: {GPS_FILE}")
    st.stop()

if stores.empty:
    st.error(f"Stores data not found or empty: {STORES_FILE}")
    st.stop()

gps.columns = gps.columns.str.strip()
stores.columns = stores.columns.str.strip()
zones.columns = zones.columns.str.strip()

for col in ["latitude", "longitude"]:
    gps[col] = pd.to_numeric(gps[col], errors="coerce")
    stores[col] = pd.to_numeric(stores[col], errors="coerce")

gps["timestamp"] = pd.to_datetime(gps["timestamp"], errors="coerce")
gps = gps.dropna(subset=["latitude", "longitude", "timestamp"])
stores = stores.dropna(subset=["latitude", "longitude"])

if gps.empty or stores.empty:
    st.error("No valid GPS records or store coordinates were found.")
    st.stop()

# -------------------------------
# 3. Dashboard heading
# -------------------------------
st.title("📍 GeoPulse")
st.subheader("Hyper-Local Retail Mobility Analytics")
st.caption(
    "Explore simulated GPS activity, store visits and "
    "overlap between retail locations."
)

# -------------------------------
# 4. Sidebar filters
# -------------------------------
st.sidebar.header("Dashboard Filters")

min_date = gps["timestamp"].dt.date.min()
max_date = gps["timestamp"].dt.date.max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered_gps = gps[
    gps["timestamp"].dt.date.between(start_date, end_date)
].copy()

areas = ["All"] + sorted(
    stores["area"].dropna().astype(str).unique().tolist()
)
selected_area = st.sidebar.selectbox("Store area", areas)

filtered_stores = stores.copy()
if selected_area != "All":
    filtered_stores = stores[
        stores["area"].astype(str) == selected_area
    ].copy()

if filtered_gps.empty:
    st.warning("No GPS records are available for this date range.")
    st.stop()

# -------------------------------
# 5. KPI cards
# -------------------------------
total_pings = len(filtered_gps)
unique_devices = filtered_gps["device_id"].nunique()
total_stores = len(filtered_stores)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total GPS Pings", f"{total_pings:,}")
col2.metric("Unique Devices", f"{unique_devices:,}")
col3.metric("Stores in Selection", f"{total_stores:,}")
col4.metric(
    "Selected Dates",
    (end_date - start_date).days + 1,
)

st.divider()

# -------------------------------
# 6. Interactive map
# -------------------------------
st.header("1. GPS Activity and Store Locations")

st.caption(
    "Blue points represent sampled GPS pings. "
    "Red points represent store locations. "
    "Zone outlines are shown when zone boundary data is available."
)

# Limit displayed GPS points to keep the map responsive.
map_gps = filtered_gps.sample(
    n=min(len(filtered_gps), 3000),
    random_state=42,
)

layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=map_gps,
        get_position="[longitude, latitude]",
        get_radius=35,
        get_fill_color=[40, 120, 220, 120],
        pickable=True,
        auto_highlight=True,
    ),
    pdk.Layer(
        "ScatterplotLayer",
        data=filtered_stores,
        get_position="[longitude, latitude]",
        get_radius=140,
        get_fill_color=[220, 60, 60, 220],
        pickable=True,
        auto_highlight=True,
    ),
]

# Draw rectangular zone outlines if the expected columns exist.
zone_columns = {
    "zone_name", "min_lat", "max_lat", "min_lon", "max_lon"
}

if not zones.empty and zone_columns.issubset(zones.columns):
    zone_paths = []

    for _, zone in zones.iterrows():
        try:
            west = float(zone["min_lon"])
            east = float(zone["max_lon"])
            south = float(zone["min_lat"])
            north = float(zone["max_lat"])

            zone_paths.append({
                "zone_name": zone["zone_name"],
                "path": [
                    [west, south],
                    [east, south],
                    [east, north],
                    [west, north],
                    [west, south],
                ],
            })
        except (TypeError, ValueError):
            continue

    if zone_paths:
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=pd.DataFrame(zone_paths),
                get_path="path",
                get_color=[20, 150, 90, 220],
                width_min_pixels=2,
                pickable=True,
            )
        )

view_state = pdk.ViewState(
    latitude=float(filtered_stores["latitude"].mean()),
    longitude=float(filtered_stores["longitude"].mean()),
    zoom=10,
    pitch=0,
)

st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            "text": "{store_name}\n{device_id}\n{zone_name}"
        },
        map_style="light",
    ),
    use_container_width=True,
)

st.caption(
    "Note: GPS points are simulated. The map shows recorded pings, "
    "not confirmed individual customer visits."
)

# -------------------------------
# 7. Hourly activity chart
# -------------------------------
st.header("2. Hourly GPS Activity")

hourly = (
    filtered_gps.assign(
        hour=filtered_gps["timestamp"].dt.hour
    )
    .groupby("hour")
    .size()
    .reset_index(name="gps_pings")
)

hourly_chart = px.line(
    hourly,
    x="hour",
    y="gps_pings",
    markers=True,
    title="GPS Pings by Hour",
    labels={
        "hour": "Hour of Day",
        "gps_pings": "Number of GPS Pings",
    },
)
st.plotly_chart(hourly_chart, use_container_width=True)

# -------------------------------
# 8. Store visit analysis
# -------------------------------
st.header("3. Store Visits and Comparison")

visits_file = PROCESSED / "store_visits.csv"
visits = load_csv(visits_file)

if not visits.empty and "store_name" in visits.columns:
    if selected_area != "All":
        visits = visits[
            visits["store_name"].isin(filtered_stores["store_name"])
        ]

    metric_col = (
        "unique_devices"
        if "unique_devices" in visits.columns
        else "total_pings"
        if "total_pings" in visits.columns
        else None
    )

    if metric_col:
        visits_chart = px.bar(
            visits.sort_values(metric_col, ascending=False),
            x="store_name",
            y=metric_col,
            title=f"Store Comparison by {metric_col.replace('_', ' ').title()}",
            labels={
                "store_name": "Store",
                metric_col: metric_col.replace("_", " ").title(),
            },
        )
        st.plotly_chart(visits_chart, use_container_width=True)

    st.dataframe(visits, use_container_width=True)
else:
    st.info(
        "Store visit report is not available yet. "
        "Run pyspark/store_cannibalization.py first."
    )

# -------------------------------
# 9. Store overlap analysis
# -------------------------------
st.header("4. Store Overlap Analysis")

overlap_file = PROCESSED / "store_overlap_pairs.csv"
overlap = load_csv(overlap_file)

if not overlap.empty:
    if "store_1" in overlap.columns and "store_2" in overlap.columns:
        overlap["Store Pair"] = (
            overlap["store_1"].astype(str)
            + " ↔ "
            + overlap["store_2"].astype(str)
        )

        value_col = (
            "shared_devices"
            if "shared_devices" in overlap.columns
            else "overlap_rate_pct"
            if "overlap_rate_pct" in overlap.columns
            else None
        )

        if value_col:
            overlap_chart = px.bar(
                overlap.sort_values(value_col, ascending=False).head(15),
                x="Store Pair",
                y=value_col,
                title=f"Store Pairs by {value_col.replace('_', ' ').title()}",
                labels={
                    "Store Pair": "Store Pair",
                    value_col: value_col.replace("_", " ").title(),
                },
            )
            st.plotly_chart(overlap_chart, use_container_width=True)

    st.dataframe(overlap, use_container_width=True)
else:
    st.info("No store overlap report found. Run the Day 9 analysis first.")

# -------------------------------
# 10. Download filtered GPS data
# -------------------------------
st.header("5. Export Filtered Data")

st.download_button(
    label="Download filtered GPS data (CSV)",
    data=filtered_gps.to_csv(index=False).encode("utf-8"),
    file_name="geopulse_filtered_gps.csv",
    mime="text/csv",
)

with st.expander("Data sources and limitations"):
    st.write(
        "- GPS data: data/raw/gps_pings.csv\n"
        "- Store locations: data/stores/stores.csv\n"
        "- Zones: data/raw/zones.csv\n"
        "- Store reports: data/processed/\n\n"
        "The dataset is simulated. A GPS ping near a store does not prove "
        "a person entered that store or made a purchase. Store overlap is "
        "a proximity-based indicator, not proof of sales cannibalization."
    )

st.caption("GeoPulse | Day 10 Dashboard")