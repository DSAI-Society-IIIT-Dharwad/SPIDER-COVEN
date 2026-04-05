import streamlit as st
import requests
import pandas as pd

st.title("🛒 Smart Scout Dashboard")

# Inputs
asin = st.text_input("Enter ASIN", "B001")
pincode = st.text_input("Enter Pincode", "500001")

# Button
if st.button("Fetch Sellers"):
    try:
        # Fetch sellers
        response = requests.get(f"http://127.0.0.1:8000/sellers/{asin}")
        data = response.json()

        if len(data) > 0:
            df = pd.DataFrame(data)

            # 🔥 Simulate location impact
            if pincode.startswith("5"):  # Example: Hyderabad
                df["delivery_days"] = df["delivery_days"] + 1
            elif pincode.startswith("1"):  # Example: Delhi
                df["delivery_days"] = df["delivery_days"]
            else:
                df["delivery_days"] = df["delivery_days"] + 2

            # Sort by price
            df = df.sort_values(by="price")

            # Highlight Buy Box
            def highlight_buybox(row):
                if row["is_buybox"]:
                    return ["background-color: lightgreen"] * len(row)
                return [""] * len(row)

            st.subheader("📊 Seller Comparison")
            st.dataframe(df.style.apply(highlight_buybox, axis=1))

            # Detect Cheapest Seller
            cheapest = df.iloc[0]

            # Detect Buy Box Seller
            buybox_seller = df[df["is_buybox"] == True]
            buybox = None

            if not buybox_seller.empty:
                buybox = buybox_seller.iloc[0]

                if buybox["seller_name"] != cheapest["seller_name"]:
                    st.warning(
                        f"⚠️ Buy Box is NOT the cheapest!\n"
                        f"Buy Box: {buybox['seller_name']} (₹{buybox['price']})\n"
                        f"Cheapest: {cheapest['seller_name']} (₹{cheapest['price']})"
                    )
                else:
                    st.success("✅ Buy Box seller is also the cheapest")

            # 🔥 Compute best seller WITH location impact
            df["score"] = df["price"] + (df["delivery_days"] * 10)
            best = df.sort_values(by="score").iloc[0]

            st.success(
                f"🏆 Best Seller: {best['seller_name']} "
                f"(₹{best['price']}, {best['delivery_days']} days)"
            )

            st.info("Selected based on price + delivery speed")

            # 🧠 Insight
            st.subheader("🧠 Insight")

            if buybox is not None:
                if buybox["seller_name"] != cheapest["seller_name"]:
                    st.info(
                        "Amazon prioritizes faster delivery or trusted sellers over lowest price."
                    )
                else:
                    st.info(
                        "Lowest price seller is also the Buy Box winner."
                    )

            # 🔥 NEW LOCATION INSIGHT
            st.subheader("📍 Location Insight")
            st.info(
                f"Delivery times and best seller may vary based on location (Pincode: {pincode})."
            )

        else:
            st.warning("No sellers found")

    except Exception as e:
        st.error("Backend not running!")
        st.text(str(e))