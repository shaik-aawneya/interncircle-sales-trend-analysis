
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    rng = np.random.default_rng(21)
    n_orders = 1500

    orders = pd.DataFrame({
        "order_date": pd.Timestamp("2025-01-01") +
        pd.to_timedelta(rng.integers(0, 365, n_orders), unit="D"),
        "customer_id": rng.integers(1001, 1301, n_orders),
        "category": rng.choice(
            ["Electronics", "Fashion", "Home", "Books"],
            n_orders,
            p=[0.30, 0.35, 0.20, 0.15]
        ),
        "amount": rng.gamma(2.2, 550, n_orders).round(2)
    })

    orders["month"] = orders["order_date"].dt.month
    orders["month_name"] = orders["order_date"].dt.month_name()
    orders["quarter"] = orders["order_date"].dt.quarter

    return orders

orders = load_data()

st.title("E-commerce Sales Analytics Dashboard")
st.caption("Project 3 | InternCircle | Sales Trend Analysis")

st.sidebar.header("Dashboard Filters")

categories = st.sidebar.multiselect(
    "Select Categories",
    orders["category"].unique(),
    default=orders["category"].unique()
)

filtered = orders[orders["category"].isin(categories)]

if filtered.empty:
    st.warning("Please select at least one category.")
    st.stop()

total_revenue = filtered["amount"].sum()
total_orders = len(filtered)
avg_order = filtered["amount"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Total Revenue", f"{total_revenue:,.2f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Average Order Value", f"{avg_order:,.2f}")

st.divider()

st.subheader("1. Monthly Revenue Trend")

monthly = (
    filtered.groupby("month")["amount"]
    .sum()
    .reindex(range(1, 13), fill_value=0)
)

monthly_growth = monthly.pct_change() * 100

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly.index, monthly.values, marker="o")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.grid(alpha=0.3)
st.pyplot(fig)
plt.close(fig)

growth_table = pd.DataFrame({
    "Month": monthly.index,
    "Revenue": monthly.values,
    "Growth (%)": monthly_growth.values
}).round(2)

st.subheader("Month-over-Month Growth")
st.dataframe(growth_table, use_container_width=True)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("2. Revenue by Category")
    category_sales = (
        filtered.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots()
    category_sales.plot(kind="bar", ax=ax)
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("3. Orders by Category")
    category_orders = filtered["category"].value_counts()

    fig, ax = plt.subplots()
    category_orders.plot(kind="bar", ax=ax)
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Orders")
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)
    plt.close(fig)

st.divider()

st.subheader("4. Top Customer Analysis")

customer_spending = (
    filtered.groupby("customer_id")["amount"]
    .sum()
    .sort_values(ascending=False)
)

top_count = max(1, int(len(customer_spending) * 0.10))
top_revenue = customer_spending.head(top_count).sum()
total_customer_revenue = customer_spending.sum()

top_share = (
    top_revenue / total_customer_revenue * 100
    if total_customer_revenue else 0
)

c1, c2 = st.columns(2)
c1.metric("Unique Customers", len(customer_spending))
c2.metric("Top 10% Revenue Share", f"{top_share:.2f}%")

st.write("Top 10 Customers by Spending")
st.dataframe(
    customer_spending.head(10).rename("Total Spending"),
    use_container_width=True
)

st.divider()

st.subheader("5. Business Insights")

best_month = monthly.idxmax()
worst_month = monthly.idxmin()
best_category = category_sales.idxmax()

month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

st.write(
    f"- Highest revenue month: {month_names[best_month - 1]} "
    f"({monthly.max():,.2f})"
)
st.write(
    f"- Lowest revenue month: {month_names[worst_month - 1]} "
    f"({monthly.min():,.2f})"
)
st.write(f"- Highest revenue category: {best_category}")
st.write(
    f"- Top 10% of customers contribute {top_share:.2f}% "
    "of the filtered revenue."
)

st.divider()

st.subheader("Dataset Preview")
st.dataframe(filtered.head(20), use_container_width=True)

st.caption(
    "Dataset: 1,500 synthetically generated fictional orders | "
    "Python, Pandas, NumPy and Matplotlib"
)
