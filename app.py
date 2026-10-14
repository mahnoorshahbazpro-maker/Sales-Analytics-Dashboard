
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Analytics Dashboard")
st.caption("Interactive sales analysis using Python, Pandas and Streamlit")

# Sample dataset
@st.cache_data
def load_sample_data():
    data = {
        "Date": [
            "2026-01-05", "2026-01-12", "2026-01-20",
            "2026-02-03", "2026-02-14", "2026-02-22",
            "2026-03-02", "2026-03-11", "2026-03-25",
            "2026-04-04", "2026-04-16", "2026-04-27",
            "2026-05-06", "2026-05-18", "2026-05-29",
            "2026-06-07", "2026-06-19", "2026-06-28"
        ],
        "Product": [
            "Laptop", "Mouse", "Keyboard", "Laptop", "Headphones",
            "Monitor", "Mouse", "Laptop", "Keyboard", "Monitor",
            "Headphones", "Laptop", "Keyboard", "Mouse", "Monitor",
            "Laptop", "Headphones", "Mouse"
        ],
        "Category": [
            "Electronics", "Accessories", "Accessories",
            "Electronics", "Accessories", "Electronics",
            "Accessories", "Electronics", "Accessories",
            "Electronics", "Accessories", "Electronics",
            "Accessories", "Accessories", "Electronics",
            "Electronics", "Accessories", "Accessories"
        ],
        "City": [
            "Lahore", "Gujranwala", "Karachi", "Islamabad",
            "Lahore", "Faisalabad", "Karachi", "Gujranwala",
            "Islamabad", "Lahore", "Faisalabad", "Karachi",
            "Gujranwala", "Lahore", "Islamabad", "Faisalabad",
            "Karachi", "Gujranwala"
        ],
        "Quantity": [2, 5, 3, 1, 4, 2, 6, 2, 4, 1, 3, 2, 5, 7, 2, 1, 4, 6],
        "Unit_Price": [
            150000, 1500, 3500, 150000, 8000, 45000,
            1500, 150000, 3500, 45000, 8000, 150000,
            3500, 1500, 45000, 150000, 8000, 1500
        ]
    }
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Revenue"] = df["Quantity"] * df["Unit_Price"]
    return df

st.sidebar.header("Dashboard Controls")
uploaded_file = st.sidebar.file_uploader(
    "Upload your sales CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required = ["Date", "Product", "Category", "City", "Quantity", "Unit_Price"]
        missing = [col for col in required if col not in df.columns]

        if missing:
            st.error("Missing required columns: " + ", ".join(missing))
            st.stop()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
        df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")
        df = df.dropna(subset=required).copy()
        df["Revenue"] = df["Quantity"] * df["Unit_Price"]

    except Exception as e:
        st.error(f"Could not read the CSV file: {e}")
        st.stop()
else:
    df = load_sample_data()

if df.empty:
    st.warning("No valid sales records to display.")
    st.stop()

st.sidebar.success(f"{len(df)} sales records loaded")

cities = sorted(df["City"].astype(str).unique())
categories = sorted(df["Category"].astype(str).unique())

selected_cities = st.sidebar.multiselect(
    "Filter by city", cities, default=cities
)
selected_categories = st.sidebar.multiselect(
    "Filter by category", categories, default=categories
)

filtered = df[
    df["City"].astype(str).isin(selected_cities)
    & df["Category"].astype(str).isin(selected_categories)
].copy()

if filtered.empty:
    st.warning("No records match your selected filters.")
    st.stop()

total_revenue = filtered["Revenue"].sum()
total_orders = len(filtered)
total_quantity = filtered["Quantity"].sum()
avg_order_value = total_revenue / total_orders if total_orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue", f"Rs {total_revenue:,.0f}")
c2.metric("🧾 Total Orders", f"{total_orders:,}")
c3.metric("📦 Units Sold", f"{total_quantity:,.0f}")
c4.metric("🛒 Average Sale", f"Rs {avg_order_value:,.0f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("📈 Monthly Revenue Trend")
    monthly = (
        filtered.assign(Month=filtered["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Revenue"].sum()
    )
    fig = px.line(
        monthly, x="Month", y="Revenue",
        markers=True, title="Revenue by Month"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🏆 Revenue by Product")
    products = (
        filtered.groupby("Product", as_index=False)["Revenue"]
        .sum().sort_values("Revenue", ascending=False)
    )
    fig = px.bar(
        products, x="Product", y="Revenue",
        color="Revenue", title="Product Performance"
    )
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    st.subheader("🏙️ Sales by City")
    city_sales = filtered.groupby("City", as_index=False)["Revenue"].sum()
    fig = px.bar(
        city_sales, x="City", y="Revenue",
        title="City-wise Revenue"
    )
    st.plotly_chart(fig, use_container_width=True)

with right2:
    st.subheader("🧩 Revenue by Category")
    category_sales = filtered.groupby("Category", as_index=False)["Revenue"].sum()
    fig = px.pie(
        category_sales, names="Category", values="Revenue",
        title="Category Revenue Share", hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Sales Data")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Sales Report",
    data=csv_data,
    file_name="sales_analytics_report.csv",
    mime="text/csv"
)

st.caption("Portfolio project • Python • Pandas • Streamlit • Plotly")
