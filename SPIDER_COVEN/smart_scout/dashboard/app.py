import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import time

API = "http://localhost:8000"

st.set_page_config(page_title="Smart Scout", layout="wide")

# Theme overrides
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Futuristic glowing buttons */
    .stButton > button { 
        border: 1px solid #00f2fe; 
        color: #00f2fe; 
        background: transparent;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover { 
        background-color: #00f2fe;
        color: #09090b;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.7);
    }
    
    /* Metric Cards - Glassmorphism */
    [data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; 
        padding: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    [data-testid="stMetricValue"] {
        color: #00f2fe;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    
    /* Dynamic Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(0, 242, 254, 0.2);
    }

    /* Sidebar Glass */
    [data-testid="stSidebar"] {
        background: rgba(17, 17, 21, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Auto refresh dashboard every 2 minutes
st_autorefresh(interval=120000, key="auto_refresh")

st.sidebar.title("🕷️ Smart Scout")

# Navigation
page = st.sidebar.radio("Navigation", ["Price Table", "Price Trends", "Alerts Feed", "Seller Leaderboard"])

st.sidebar.divider()
st.sidebar.subheader("Controls")

try:
    asins_for_crawl = requests.get(f"{API}/asins").json()
    crawl_asin = st.sidebar.selectbox(
        "ASIN to crawl", [r["asin"] for r in asins_for_crawl] if asins_for_crawl else ["B07SKKG51W"], key="crawl_asin"
    )
except Exception:
    crawl_asin = "B07SKKG51W"

PIN_MAP_CRAWL = {"Chennai": "600001", "Delhi": "110001"}
crawl_pin = PIN_MAP_CRAWL[st.sidebar.selectbox("Pincode", list(PIN_MAP_CRAWL.keys()), key="crawl_pin")]

if st.sidebar.button("Crawl Now"):
    with st.spinner("Scraping..."):
        try:
            r = requests.post(f"{API}/crawl?asin={crawl_asin}&pin={crawl_pin}")
            if r.status_code == 200:
                time.sleep(5)   # wait for spider to return some data
                st.sidebar.success("Done — refresh to see new data")
            else:
                st.sidebar.error("Crawl failed — check terminal")
        except Exception:
            st.sidebar.error("Failed to trigger crawl on API")

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
