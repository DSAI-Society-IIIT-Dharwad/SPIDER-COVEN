import streamlit as st
import requests
import time
from streamlit_autorefresh import st_autorefresh

API = "http://localhost:8000"

st.set_page_config(
    page_title="Smart Scout",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Clean Minimalist Typography */
    * { font-family: 'Inter', sans-serif !important; }
    
    /* Green Accent Buttons */
    .stButton > button { 
        border-color: #00D26A; 
        color: #00D26A; 
        background-color: transparent;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        background-color: #00D26A; 
        color: #0A0A0A;
        box-shadow: 0 4px 15px rgba(0, 210, 106, 0.2); 
    }
    
    /* Sleek Metric Cards */
    [data-testid="metric-container"] { 
        background: #141414; 
        border: 1px solid #1F1F1F;
        border-right: 3px solid #00D26A;
        border-radius: 6px; 
        padding: 15px; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar nav
page = st.sidebar.radio(
    "Navigate",
    ["Price Table", "Price Trends", "Alerts Feed", "Seller Leaderboard"]
)

# Auto Refresh & Crawl logic
st_autorefresh(interval=120000, key="auto_refresh")

st.sidebar.divider()
st.sidebar.subheader("Controls")

try:
    asins_for_crawl = requests.get(f"{API}/asins").json()
except Exception:
    asins_for_crawl = []

if asins_for_crawl:
    crawl_asin = st.sidebar.selectbox(
        "ASIN to crawl", [r["asin"] for r in asins_for_crawl], key="crawl_asin"
    )
    PIN_MAP_CRAWL = {"Chennai": "600001", "Delhi": "110001"}
    crawl_pin = PIN_MAP_CRAWL[st.sidebar.selectbox("Pincode", list(PIN_MAP_CRAWL.keys()), key="crawl_pin")]

    if st.sidebar.button("Crawl Now"):
        with st.spinner("Scraping..."):
            r = requests.post(f"{API}/crawl?asin={crawl_asin}&pin={crawl_pin}")
            if r.status_code == 200:
                time.sleep(5)   # wait for spider to return some data
                st.sidebar.success("Done — refresh to see new data")
            else:
                st.sidebar.error("Crawl failed — check terminal")

# Page routing
if page == "Price Table":
    from dashboard.pages.price_table import render
    render()
elif page == "Price Trends":
    from dashboard.pages.trends import render
    render()
elif page == "Alerts Feed":
    from dashboard.pages.alerts import render
    render()
elif page == "Seller Leaderboard":
    from dashboard.pages.leaderboard import render
    render()