import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.kpi-card {
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,.25);
    background: rgba(128,128,128,.06);
    min-height: 105px;
}
.kpi-label {font-size: .85rem; opacity: .7;}
.kpi-value {font-size: 1.35rem; font-weight: 700; margin-top: .35rem;}
.insight {
    padding: .75rem 1rem;
    border-left: 4px solid #4f46e5;
    background: rgba(79,70,229,.07);
    border-radius: 6px;
    margin-bottom: .5rem;
}
</style>
""", unsafe_allow_html=True)

REQUIRED_COLUMNS = [
    "sales", "order_profit_per_order", "order_item_quantity",
    "customer_id", "customer_segment", "category_name",
    "product_name", "market", "order_region", "order_country",
    "shipping_mode", "late_delivery_risk", "order_item_discount",
    "order_item_discount_rate", "product_price",
    "order_item_profit_ratio", "order_item_total"
]

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    return df

def validate_dataset(df):
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]

def money(x):
    return f"{x:,.2f}" if pd.notna(x) else "N/A"

def margin(profit, revenue):
    return (profit / revenue * 100) if revenue else 0.0

def kpi(label, value):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True
    )

def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)

def apply_filters(df, filters):
    out = df
    for col, vals in filters.items():
        if vals:
            out = out[out[col].astype(str).isin(vals)]
    return out

# Upload screen
if "data" not in st.session_state:
    st.title("Supply Chain Revenue, Profitability & Customer Analytics")
    st.caption("Upload the cleaned APL Logistics CSV to begin.")

    uploaded_file = st.file_uploader(
        "Upload APL_Logistics_cleaned.csv",
        type=["csv"],
        help="Upload the cleaned supply-chain dataset."
    )

    if uploaded_file is None:
        st.info("Upload your CSV to unlock the dashboard.")
        st.markdown("""
        **Dashboard modules**
        - Revenue & Profit Overview
        - Customer Value Dashboard
        - Product & Category Performance
        - Discount Impact Analyzer
        - What-if discount scenarios
        """)
        st.stop()

    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the CSV: {e}")
        st.stop()

    missing = validate_dataset(df)
    if missing:
        st.error("The uploaded dataset is missing required columns:")
        st.write(", ".join(f"`{c}`" for c in missing))
        st.stop()

    st.session_state["data"] = df

df = st.session_state["data"]

st.title("Supply Chain Revenue, Profitability & Customer Analytics")
st.success(f"Dataset loaded successfully — {len(df):,} records and {df.shape[1]} columns.")

# Sidebar
st.sidebar.title("Supply Chain Analytics")
page = st.sidebar.radio(
    "Dashboard Module",
    [
        "Revenue & Profit Overview",
        "Customer Value Dashboard",
        "Product & Category Performance",
        "Discount Impact Analyzer"
    ]
)

filter_columns = {
    "Market": "market",
    "Order Region": "order_region",
    "Order Country": "order_country",
    "Customer Segment": "customer_segment",
    "Category": "category_name",
    "Product": "product_name",
    "Shipping Mode": "shipping_mode"
}

filters = {}
st.sidebar.subheader("Global Filters")
for label, col in filter_columns.items():
    values = sorted(df[col].dropna().astype(str).unique().tolist())
    filters[col] = st.sidebar.multiselect(label, values)

if st.sidebar.button("Reset Filters"):
    st.session_state.pop("data", None)
    st.rerun()

filtered = apply_filters(df, filters)
st.sidebar.metric("Filtered Records", f"{len(filtered):,}")

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ============================================================
# PAGE 1 — REVENUE & PROFIT
# ============================================================
if page == "Revenue & Profit Overview":
    st.header("Revenue & Profit Overview")

    total_sales = filtered["sales"].sum()
    total_profit = filtered["order_profit_per_order"].sum()
    total_margin = margin(total_profit, total_sales)
    transactions = len(filtered)
    units = filtered["order_item_quantity"].sum()
    aov = total_sales / transactions if transactions else 0

    cols = st.columns(6)
    for c, label, value in zip(
        cols,
        ["Total Sales", "Total Profit", "Profit Margin", "Transactions", "Units Sold", "Average Order Value"],
        [money(total_sales), money(total_profit), f"{total_margin:.2f}%",
         f"{transactions:,}", f"{units:,.0f}", money(aov)]
    ):
        with c:
            kpi(label, value)

    st.divider()

    market = filtered.groupby("market").agg(
        sales=("sales", "sum"),
        profit=("order_profit_per_order", "sum"),
        transactions=("market", "size")
    ).reset_index()
    market["profit_margin"] = np.where(
        market["sales"] != 0, market["profit"] / market["sales"] * 100, 0
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(market.sort_values("sales", ascending=False),
                     x="market", y="sales", title="Revenue by Market")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(market.sort_values("profit", ascending=False),
                     x="market", y="profit", title="Profit by Market")
        st.plotly_chart(fig, use_container_width=True)

    category = filtered.groupby("category_name").agg(
        sales=("sales", "sum"),
        profit=("order_profit_per_order", "sum"),
        transactions=("category_name", "size")
    ).reset_index()
    category["profit_margin"] = np.where(
        category["sales"] != 0, category["profit"] / category["sales"] * 100, 0
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            category, x="sales", y="profit", size="transactions",
            color="profit_margin", hover_name="category_name",
            title="Revenue vs Profitability by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        low = category.nsmallest(10, "profit_margin")
        fig = px.bar(
            low.sort_values("profit_margin"),
            x="profit_margin", y="category_name", orientation="h",
            title="Lowest-Margin Categories"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Key Business Insights")
    insight(f"Highest-revenue market: <b>{market.loc[market.sales.idxmax(), 'market']}</b>.")
    insight(f"Highest-profit market: <b>{market.loc[market.profit.idxmax(), 'market']}</b>.")
    insight(f"Highest-margin category: <b>{category.loc[category.profit_margin.idxmax(), 'category_name']}</b>.")
    insight(f"Lowest-margin category: <b>{category.loc[category.profit_margin.idxmin(), 'category_name']}</b>.")
    st.caption("The supplied dataset has no usable order-date field, so no fabricated monthly trend is shown.")

# ============================================================
# PAGE 2 — CUSTOMER VALUE
# ============================================================
elif page == "Customer Value Dashboard":
    st.header("Customer Value Dashboard")

    customer = filtered.groupby(["customer_id", "customer_segment"]).agg(
        revenue=("sales", "sum"),
        profit=("order_profit_per_order", "sum"),
        transactions=("customer_id", "size")
    ).reset_index()
    customer["profit_margin"] = np.where(
        customer["revenue"] != 0, customer["profit"] / customer["revenue"] * 100, 0
    )

    cols = st.columns(5)
    values = [
        f"{customer.customer_id.nunique():,}",
        money(customer.revenue.mean()),
        money(customer.profit.mean()),
        money(customer.profit.max()),
        money(customer.profit.min())
    ]
    labels = [
        "Total Customers", "Avg Customer Revenue", "Avg Customer Profit",
        "Highest Customer Profit", "Lowest Customer Profit"
    ]
    for c, label, value in zip(cols, labels, values):
        with c:
            kpi(label, value)

    c1, c2 = st.columns(2)
    with c1:
        top = customer.nlargest(10, "profit").sort_values("profit")
        fig = px.bar(top, x="profit", y="customer_id", orientation="h",
                     title="Top 10 Customers by Profit")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        bottom = customer.nsmallest(10, "profit").sort_values("profit")
        fig = px.bar(bottom, x="profit", y="customer_id", orientation="h",
                     title="Bottom 10 Customers by Profit")
        st.plotly_chart(fig, use_container_width=True)

    segment = filtered.groupby("customer_segment").agg(
        customers=("customer_id", "nunique"),
        revenue=("sales", "sum"),
        profit=("order_profit_per_order", "sum")
    ).reset_index()
    segment["profit_margin"] = np.where(
        segment["revenue"] != 0, segment["profit"] / segment["revenue"] * 100, 0
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(segment, x="customer_segment", y="revenue",
                     title="Customer Segment Revenue Contribution")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(segment, x="customer_segment", y="profit",
                     title="Customer Segment Profit Contribution")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        customer, x="revenue", y="profit", size="transactions",
        color="customer_segment", hover_data=["customer_id", "profit_margin"],
        title="Customer Value Matrix"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Segment Profitability")
    st.dataframe(segment.sort_values("profit", ascending=False),
                 use_container_width=True, hide_index=True)

    st.subheader("Key Business Insights")
    insight(f"Most profitable segment: <b>{segment.loc[segment.profit.idxmax(), 'customer_segment']}</b>.")
    insight(f"Weakest-margin segment: <b>{segment.loc[segment.profit_margin.idxmin(), 'customer_segment']}</b>.")

# ============================================================
# PAGE 3 — PRODUCT & CATEGORY
# ============================================================
elif page == "Product & Category Performance":
    st.header("Product & Category Performance")

    product = filtered.groupby("product_name").agg(
        revenue=("sales", "sum"),
        profit=("order_profit_per_order", "sum"),
        quantity=("order_item_quantity", "sum"),
        discount=("order_item_discount_rate", "mean")
    ).reset_index()
    product["profit_margin"] = np.where(
        product["revenue"] != 0, product["profit"] / product["revenue"] * 100, 0
    )
    product["discount"] *= 100

    category = filtered.groupby("category_name").agg(
        revenue=("sales", "sum"),
        profit=("order_profit_per_order", "sum"),
        quantity=("order_item_quantity", "sum"),
        discount=("order_item_discount_rate", "mean")
    ).reset_index()
    category["profit_margin"] = np.where(
        category["revenue"] != 0, category["profit"] / category["revenue"] * 100, 0
    )
    category["discount"] *= 100

    cols = st.columns(5)
    vals = [
        f"{product.product_name.nunique():,}",
        f"{category.category_name.nunique():,}",
        product.loc[product.revenue.idxmax(), "product_name"],
        product.loc[product.profit.idxmax(), "product_name"],
        category.loc[category.profit_margin.idxmax(), "category_name"]
    ]
    labels = [
        "Total Products", "Total Categories", "Best-Selling Product",
        "Most Profitable Product", "Highest-Margin Category"
    ]
    for c, label, value in zip(cols, labels, vals):
        with c:
            kpi(label, str(value))

    c1, c2 = st.columns(2)
    with c1:
        top = product.nlargest(15, "revenue").sort_values("revenue")
        fig = px.bar(top, x="revenue", y="product_name", orientation="h",
                     title="Top 15 Products by Revenue")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        top_profit = product.nlargest(15, "profit").sort_values("profit")
        fig = px.bar(top_profit, x="profit", y="product_name", orientation="h",
                     title="Top 15 Products by Profit")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product-Level Margin Analysis")
    st.dataframe(
        product[["product_name", "revenue", "profit", "profit_margin", "quantity", "discount"]]
        .sort_values("profit_margin", ascending=False),
        use_container_width=True, hide_index=True
    )

    st.subheader("Category Profitability Heatmap")
    heat = category.set_index("category_name")[
        ["revenue", "profit", "profit_margin", "quantity", "discount"]
    ]
    fig = px.imshow(
        heat, aspect="auto", color_continuous_scale="RdYlGn",
        title="Category Profitability Heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)

    revenue_median = category.revenue.median()
    profit_median = category.profit.median()
    category["performance"] = np.select(
        [
            (category.revenue >= revenue_median) & (category.profit >= profit_median),
            (category.revenue >= revenue_median) & (category.profit < profit_median),
            (category.revenue < revenue_median) & (category.profit >= profit_median)
        ],
        [
            "High Revenue / High Profit",
            "High Revenue / Low Profit",
            "Low Revenue / High Profit"
        ],
        default="Low Revenue / Low Profit"
    )

    st.subheader("Category Performance Matrix")
    st.dataframe(
        category[["category_name", "revenue", "profit", "profit_margin", "performance"]]
        .sort_values("revenue", ascending=False),
        use_container_width=True, hide_index=True
    )

# ============================================================
# PAGE 4 — DISCOUNT IMPACT
# ============================================================
else:
    st.header("Discount Impact Analyzer")
    st.caption("Correlation and scenario analysis for discounting and profitability.")

    analysis = filtered.copy()
    analysis["profit_margin"] = np.where(
        analysis["sales"] != 0,
        analysis["order_profit_per_order"] / analysis["sales"] * 100,
        0
    )
    analysis["discount_pct"] = analysis["order_item_discount_rate"] * 100

    level = st.radio("Analyze by", ["All Data", "Category", "Market"], horizontal=True)

    if level == "Category":
        choices = sorted(analysis.category_name.dropna().astype(str).unique())
        choice = st.selectbox("Select Category", choices)
        analysis = analysis[analysis.category_name.astype(str) == choice]
    elif level == "Market":
        choices = sorted(analysis.market.dropna().astype(str).unique())
        choice = st.selectbox("Select Market", choices)
        analysis = analysis[analysis.market.astype(str) == choice]

    plot_data = analysis.sample(min(12000, len(analysis)), random_state=42)

    fig = px.scatter(
        plot_data, x="discount_pct", y="order_profit_per_order",
        hover_data=["product_name", "category_name", "market"],
        opacity=.45, title="Discount vs Profit"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        plot_data, x="discount_pct", y="profit_margin",
        hover_data=["product_name", "category_name", "market"],
        opacity=.45, title="Discount vs Profit Margin"
    )
    st.plotly_chart(fig, use_container_width=True)

    bins = [-.01, 10, 20, 30, 40, np.inf]
    labels = ["0–10%", "10–20%", "20–30%", "30–40%", "40%+"]
    analysis["discount_band"] = pd.cut(
        analysis.discount_pct, bins=bins, labels=labels
    )

    summary = analysis.groupby("discount_band", observed=False).agg(
        transactions=("discount_band", "size"),
        average_revenue=("sales", "mean"),
        average_profit=("order_profit_per_order", "mean"),
        average_margin=("profit_margin", "mean")
    ).reset_index()

    st.subheader("Discount Bands")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    profit_corr = analysis.order_item_discount_rate.corr(
        analysis.order_profit_per_order
    )
    margin_corr = analysis.order_item_discount_rate.corr(
        analysis.profit_margin
    )

    low_margin = analysis.loc[
        analysis.order_item_discount_rate <= .10, "profit_margin"
    ].mean()
    high_margin = analysis.loc[
        analysis.order_item_discount_rate >= .40, "profit_margin"
    ].mean()

    cols = st.columns(4)
    vals = [
        f"{profit_corr:.3f}",
        f"{margin_corr:.3f}",
        f"{low_margin:.2f}%" if pd.notna(low_margin) else "N/A",
        f"{high_margin:.2f}%" if pd.notna(high_margin) else "N/A"
    ]
    labels = [
        "Discount ↔ Profit Correlation",
        "Discount ↔ Margin Correlation",
        "Avg Margin ≤10% Discount",
        "Avg Margin ≥40% Discount"
    ]
    for c, label, value in zip(cols, labels, vals):
        with c:
            kpi(label, value)

    st.info("Correlation indicates association, not causation.")

    st.divider()
    st.subheader("What-If Discount Scenario")

    scenario_level = st.radio(
        "Scenario Level", ["Product", "Category"], horizontal=True
    )
    scenario_col = "product_name" if scenario_level == "Product" else "category_name"

    choices = sorted(filtered[scenario_col].dropna().astype(str).unique())
    selected = st.selectbox(f"Select {scenario_level}", choices)
    target = filtered[filtered[scenario_col].astype(str) == selected]

    current_discount = float(target.order_item_discount_rate.mean())
    scenario_discount = st.slider(
        "Scenario Discount (%)",
        0.0, 80.0,
        float(min(current_discount * 100, 80)),
        0.5
    ) / 100

    quantity = st.number_input(
        "Scenario Quantity", min_value=1, value=1, step=1
    )

    avg_price = target.product_price.mean()
    if pd.isna(avg_price) or avg_price <= 0:
        avg_price = (
            target.order_item_total.sum()
            / max(target.order_item_quantity.sum(), 1)
        )

    avg_profit_ratio = target.order_item_profit_ratio.mean()

    current_revenue = avg_price * quantity * (1 - current_discount)
    scenario_revenue = avg_price * quantity * (1 - scenario_discount)

    current_profit = current_revenue * avg_profit_ratio
    scenario_profit = scenario_revenue * avg_profit_ratio

    current_margin = margin(current_profit, current_revenue)
    scenario_margin = margin(scenario_profit, scenario_revenue)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Current")
        kpi("Revenue", money(current_revenue))
        kpi("Estimated Profit", money(current_profit))
        kpi("Profit Margin", f"{current_margin:.2f}%")
    with c2:
        st.subheader("Scenario")
        kpi("Revenue", money(scenario_revenue))
        kpi("Estimated Profit", money(scenario_profit))
        kpi("Profit Margin", f"{scenario_margin:.2f}%")

    comparison = pd.DataFrame({
        "Scenario": ["Current", "Scenario"],
        "Revenue": [current_revenue, scenario_revenue],
        "Estimated Profit": [current_profit, scenario_profit]
    })

    fig = px.bar(
        comparison, x="Scenario",
        y=["Revenue", "Estimated Profit"],
        barmode="group",
        title="Current vs Scenario"
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("Profit Change", money(scenario_profit - current_profit))
    with c2:
        kpi("Margin Change", f"{scenario_margin - current_margin:.2f} pp")
    with c3:
        revenue_change = (
            (scenario_revenue - current_revenue) / current_revenue * 100
            if current_revenue else 0
        )
        kpi("Revenue Change", f"{revenue_change:.2f}%")

    st.warning(
        "This is an analytical what-if estimate, not a financial forecast. "
        "It assumes the observed profit ratio remains constant."
    )

st.divider()
st.caption("Supply Chain Analytics | Data Science Project")
