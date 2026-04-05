import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

def render():
    st.title("Price comparison")

    # Sidebar controls
    try:
        asins_resp = requests.get(f"{API}/asins").json()
        asin_options = {r["title"]: r["asin"] for r in asins_resp} if asins_resp else {}
    except Exception:
        st.error("Cannot connect to FastAPI backend.")
        return

    if not asin_options:
        st.info("No data yet — run a spider first or click Crawl Now in the sidebar.")
        return

    selected_title = st.sidebar.selectbox("Product (ASIN)", list(asin_options.keys()))
    asin = asin_options[selected_title]

    PIN_MAP = {"Chennai (600001)": "600001", "Delhi (110001)": "110001",
               "Hyderabad (500001)": "500001", "Mumbai (400001)": "400001"}
    pin_label = st.sidebar.selectbox("Buyer location", list(PIN_MAP.keys()))
    pin = PIN_MAP[pin_label]

    # Standard empty state guard
    data = requests.get(f"{API}/prices/{asin}?pin={pin}").json()
    if not data:
        st.info("No data for this selection. Use 'Crawl Now' in the sidebar to fetch live prices.")
        if st.button("Trigger crawl now", key="pt_crawl"):
            requests.post(f"{API}/crawl?asin={asin}&pin={pin}")
            st.success("Crawl started — check back in 30 seconds")
        st.stop()

    df = pd.DataFrame(data)
    df = df[["seller","price","shipping","net_price","is_buy_box","is_fba","stock_left","scraped_at"]]
    df.columns = ["Seller","Price (₹)","Shipping (₹)","Net Price (₹)","Buy Box","FBA","Stock Left","Scraped At"]
    df = df.sort_values("Net Price (₹)")

    def highlight_bb(row):
        return ["background-color:#E1F5EE; color:#085041" if row["Buy Box"]
                else "" for _ in row]

    st.dataframe(
        df.style.apply(highlight_bb, axis=1),
        use_container_width=True, hide_index=True
    )
    st.caption(f"Showing latest prices for {asin} · {pin_label}")
