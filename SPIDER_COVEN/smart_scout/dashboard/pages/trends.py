import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

API = "http://localhost:8000"
PIN_MAP = {"Chennai": "600001", "Delhi": "110001",
           "Hyderabad": "500001", "Mumbai": "400001"}

def render():
    st.title("Price trends & Buy Box geography")

    try:
        asins = requests.get(f"{API}/asins").json()
    except Exception:
        st.error("Cannot connect to FastAPI backend.")
        return

    if not asins:
        st.info("No data yet."); return
    asin_map = {r["title"]: r["asin"] for r in asins}
    asin = asin_map[st.sidebar.selectbox("Product", list(asin_map.keys()))]

    # Standard empty state guard
    data = requests.get(f"{API}/prices/{asin}").json()
    if not data:
        st.info("No data for this selection. Use 'Crawl Now' in the sidebar to fetch live prices.")
        if st.button("Trigger crawl now", key="trends_crawl"):
            requests.post(f"{API}/crawl?asin={asin}&pin=600001")
            st.success("Crawl started — check back in 30 seconds")
        st.stop()

    # --- Price trend chart ---
    st.subheader("Interactive Trend")
    all_data = []
    for pin_label, pin in PIN_MAP.items():
        rows = requests.get(f"{API}/prices/{asin}?pin={pin}").json()
        for r in rows:
            r["location"] = pin_label
            all_data.append(r)

    if all_data:
        df = pd.DataFrame(all_data)
        df["scraped_at"] = pd.to_datetime(df["scraped_at"])
        
        # New M4-2 widgets
        col_w1, col_w2 = st.columns(2)
        min_date = df["scraped_at"].min().date()
        max_date = df["scraped_at"].max().date()
        
        selected_dates = col_w1.date_input("Date range", [min_date, max_date])
        show_pin_lines = col_w2.checkbox("Show broken by location (dashed)", value=True)

        if len(selected_dates) == 2:
            start_d, end_d = selected_dates
            df = df[(df["scraped_at"].dt.date >= start_d) & (df["scraped_at"].dt.date <= end_d)]

        line_dash = "location" if show_pin_lines else None
        
        fig = px.line(df, x="scraped_at", y="net_price",
                      color="seller", line_dash=line_dash, template="plotly_dark",
                      color_discrete_sequence=px.colors.qualitative.Set2,
                      title="Net price over time")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Buy Box heatmap ---
    st.subheader("Buy Box geography — who wins where")
    hmap_rows = []
    for pin_label, pin in PIN_MAP.items():
        rows = requests.get(f"{API}/prices/{asin}?pin={pin}").json()
        bb_rows = [r for r in rows if r.get("is_buy_box")]
        if bb_rows:
            winner = bb_rows[0]["seller"]
            for seller in set(r["seller"] for r in rows):
                hmap_rows.append({"Location": pin_label, "Seller": seller,
                                  "Wins Box": 1 if seller == winner else 0})

    if hmap_rows:
        hdf = pd.DataFrame(hmap_rows)
        pivot = hdf.pivot_table(index="Location", columns="Seller",
                                values="Wins Box", aggfunc="max").fillna(0)
        fig2 = px.imshow(pivot, color_continuous_scale="Tealgrn", template="plotly_dark",
                         labels={"color": "Holds Buy Box"},
                         title="Buy Box winner by location")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Run crawls with multiple pincodes to see the heatmap.")
