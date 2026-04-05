import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API = "http://localhost:8000"
PIN_MAP = {"Chennai": "600001", "Delhi": "110001",
           "Hyderabad": "500001", "Mumbai": "400001"}

def render():
    st.title("Seller leaderboard")

    asins = requests.get(f"{API}/asins").json()
    if not asins:
        st.info("No data yet."); return
    asin_map = {r["title"]: r["asin"] for r in asins}
    asin = asin_map[st.sidebar.selectbox("Product", list(asin_map.keys()))]
    pin_label = st.sidebar.selectbox("Location", list(PIN_MAP.keys()))
    pin = PIN_MAP[pin_label]

    # Standard empty state guard
    data = requests.get(f"{API}/prices/{asin}?pin={pin}").json()
    if not data:
        st.info("No data for this selection. Use 'Crawl Now' in the sidebar to fetch live prices.")
        if st.button("Trigger crawl now"):
            requests.post(f"{API}/crawl?asin={asin}&pin={pin}")
            st.success("Crawl started — check back in 30 seconds")
        st.stop()

    # Winning Gap recommendation
    gap_data = requests.get(f"{API}/winning_gap/{asin}?pin={pin}").json()
    if gap_data.get("gap") is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("Your net price", f"₹{gap_data['your_price']:.0f}")
        col2.metric("Competitor min", f"₹{gap_data['competitor_min']:.0f}")
        col3.metric("Gap", f"₹{abs(gap_data['gap']):.0f}",
                    delta=gap_data["recommendation"],
                    delta_color="inverse" if gap_data["gap"] > 0 else "normal")

    st.divider()

    # Leaderboard
    df = pd.DataFrame(data)
    wr = df.groupby("seller")["is_buy_box"].mean().reset_index()
    wr.columns = ["Seller", "Win Rate"]
    wr["Win %"] = (wr["Win Rate"] * 100).round(1)
    wr = wr.sort_values("Win Rate", ascending=True)

    fig = px.bar(wr, x="Win %", y="Seller", orientation="h",
                 color="Win %", color_continuous_scale="Tealgrn", template="plotly_dark",
                 title="Buy Box win rate per seller")
    st.plotly_chart(fig, use_container_width=True)
