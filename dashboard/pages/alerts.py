import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

def render():
    st.title("Alerts feed")

    try:
        data = requests.get(f"{API}/alerts").json()
    except Exception:
        st.error("Backend offline")
        return

    if not data:
        st.info("No alerts yet — run analysis after a crawl.")
        return

    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])

    sev_colors = {"HIGH": "red", "MED": "orange", "LOW": "green"}
    for _, row in df.iterrows():
        color = sev_colors.get(row["severity"], "gray")
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 2])
            col1.markdown(f":{color}[**{row['severity']}**]")
            col2.write(row["message"])
            col3.caption(row["created_at"].strftime("%H:%M %d %b"))
        st.divider()
