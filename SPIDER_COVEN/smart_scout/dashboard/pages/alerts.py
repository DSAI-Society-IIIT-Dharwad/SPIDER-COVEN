import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

def render():
    st.title("Alerts feed")

    # Standard empty state guard
    data = requests.get(f"{API}/alerts").json()
    if not data:
        st.info("No alerts yet — run analysis after a crawl.")
        return

    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Futuristic Severity badge colors
    sev_colors = {"HIGH": "#ff2a2a", "MED": "#ffaa00", "LOW": "#00f2fe"}
    for _, row in df.iterrows():
        color = sev_colors.get(row["severity"], "gray")
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 2])
            badge_html = f'''
            <div style="border: 1px solid {color}; color: {color}; padding: 4px 8px; border-radius: 4px; text-align: center; font-weight: bold; text-shadow: 0 0 5px {color}; box-shadow: 0 0 10px {color}33; display: inline-block;">
                {row["severity"]}
            </div>
            '''
            col1.markdown(badge_html, unsafe_allow_html=True)
            col2.write(row["message"])
            col3.caption(row["created_at"].strftime("%H:%M %d %b"))
        st.divider()
