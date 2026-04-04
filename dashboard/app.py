import streamlit as st
import requests
import pandas as pd

st.title("🛒 Smart Scout Dashboard")

# Input
asin = st.text_input("Enter ASIN", "B001")

# Button
if st.button("Fetch Sellers"):
    try:
        response = requests.get(f"http://127.0.0.1:8000/sellers/{asin}")
        data = response.json()

        if len(data) > 0:
            df = pd.DataFrame(data)

            # Sort by price
            df = df.sort_values(by="price")

            # Highlight Buy Box
            def highlight_buybox(row):
                if row["is_buybox"]:
                    return ["background-color: lightgreen"] * len(row)
                return [""] * len(row)

            st.dataframe(df.style.apply(highlight_buybox, axis=1))

            # Show best seller
            best = df.iloc[0]
            st.success(f"🏆 Best Seller: {best['seller_name']} at ₹{best['price']}")

        else:
            st.warning("No sellers found")

    except:
        st.error("Backend not running!")