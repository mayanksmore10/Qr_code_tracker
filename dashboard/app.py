import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="QR-Tracker Analytics",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from data_loader import load_visits
except RuntimeError as _db_err:
    st.error(f"**Database configuration error**\n\n{_db_err}")
    st.info("Tip: make sure `Qr_code_tracker/.env` contains `DATABASE_URL=...` and that PostgreSQL is running.")
    st.stop()

from charts import visits_over_time, top_places, device_distribution, date_hour_heatmap

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
    }
    h1 { color: #38bdf8; }
    h2, h3 { color: #7dd3fc; }
    .main { background-color: #0b1120; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=120, show_spinner="Loading visit data…")
def get_data():
    df = load_visits()
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

df = get_data()

if df.empty:
    st.warning("⚠️ No visit records found. Check your database connection or seed some data first.")
    st.stop()

st.title("📍 QR-Tracker Analytics Dashboard")
st.caption(f"Showing **{len(df):,}** visit records · Last updated: {pd.Timestamp.now().strftime('%d %b %Y, %H:%M')}")
st.divider()

col1, col2, col3, col4 = st.columns(4)
total_visits   = len(df)
unique_places  = df["place"].nunique()
unique_suburbs = df["suburb"].nunique()
mobile_pct     = round(df["device_type"].eq("Mobile").sum() / total_visits * 100, 1)
col1.metric("🏷️ Total Visits",    f"{total_visits:,}")
col2.metric("📌 Unique Places",   f"{unique_places}")
col3.metric("🗺️ Suburbs Covered", f"{unique_suburbs}")
col4.metric("📱 Mobile Share",    f"{mobile_pct}%")

st.divider()

st.subheader("📈 Visits Over Time")
fig_time = visits_over_time(df)
st.pyplot(fig_time, use_container_width=True)
plt.close(fig_time)

st.divider()

col_left, col_right = st.columns([3, 2])
with col_left:
    st.subheader("🏙️ Top Places by Visits")
    fig_places = top_places(df, place_col="suburb", top_n=7)
    st.pyplot(fig_places, use_container_width=True)
    plt.close(fig_places)

with col_right:
    st.subheader("📱 Device Type Distribution")
    fig_device = device_distribution(df)
    st.pyplot(fig_device, use_container_width=True)
    plt.close(fig_device)

st.divider()

st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)
st.subheader("🔥 Visit Activity Heatmap (Date × Hour)")
fig_heat = date_hour_heatmap(df)
st.pyplot(fig_heat, use_container_width=True)
plt.close(fig_heat)

