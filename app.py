import streamlit as st
import plotly.express as px
import pandas as pd
from agent import ask_agent
from db import run_query

st.set_page_config(
    page_title="Sales AI Agent",
    page_icon="📊",
    layout="wide"
)

# ── Auto chart function (defined first) ───────────────────
def auto_chart(question: str):
    q = question.lower()
    try:
        if any(w in q for w in ["month", "trend", "over time", "last 5"]):
            df = run_query("""
                SELECT strftime('%Y-%m', order_date) as month,
                       ROUND(SUM(total_amount), 2) as revenue
                FROM orders
                GROUP BY month ORDER BY month
            """)
            if df.empty:
                return None
            fig = px.line(
                df, x="month", y="revenue",
                title="Monthly revenue trend",
                markers=True,
                labels={"month": "Month", "revenue": "Revenue ($)"}
            )
            fig.update_traces(line_color="#7F77DD", line_width=3)
            return fig

        elif any(w in q for w in ["product", "top", "highest", "best"]):
            df = run_query("""
                SELECT p.product_name,
                       ROUND(SUM(o.total_amount), 2) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.product_name
                ORDER BY revenue DESC
            """)
            if df.empty:
                return None
            return px.bar(
                df, x="product_name", y="revenue",
                title="Revenue by product",
                color="revenue",
                color_continuous_scale="Blues",
                labels={"product_name": "Product", "revenue": "Revenue ($)"}
            )

        elif any(w in q for w in ["region", "area", "location"]):
            df = run_query("""
                SELECT c.region,
                       ROUND(SUM(o.total_amount), 2) as revenue
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.region ORDER BY revenue DESC
            """)
            if df.empty:
                return None
            return px.pie(
                df, names="region", values="revenue",
                title="Revenue by region",
                hole=0.4
            )

        elif any(w in q for w in ["customer", "who", "buyer", "spent"]):
            df = run_query("""
                SELECT c.customer_name,
                       ROUND(SUM(o.total_amount), 2) as revenue
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.customer_name ORDER BY revenue DESC
            """)
            if df.empty:
                return None
            return px.bar(
                df, x="customer_name", y="revenue",
                title="Revenue by customer",
                color="revenue",
                color_continuous_scale="Oranges",
                labels={"customer_name": "Customer", "revenue": "Revenue ($)"}
            )

        elif any(w in q for w in ["category", "type"]):
            df = run_query("""
                SELECT p.category,
                       ROUND(SUM(o.total_amount), 2) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.category ORDER BY revenue DESC
            """)
            if df.empty:
                return None
            return px.pie(
                df, names="category", values="revenue",
                title="Revenue by category",
                hole=0.4
            )

        else:
            df = run_query("""
                SELECT strftime('%Y-%m', order_date) as month,
                       ROUND(SUM(total_amount), 2) as revenue
                FROM orders
                GROUP BY month ORDER BY month
            """)
            if df.empty:
                return None
            fig = px.line(
                df, x="month", y="revenue",
                title="Overall sales trend",
                markers=True,
                labels={"month": "Month", "revenue": "Revenue ($)"}
            )
            fig.update_traces(line_color="#1D9E75", line_width=3)
            return fig

    except Exception as e:
        st.error(f"Chart error: {str(e)}")
        return None


# ── Dashboard chart function ──────────────────────────────
def show_dashboard_chart(chart_type: str):
    try:
        if chart_type == "product":
            df = run_query("""
                SELECT p.product_name,
                       ROUND(SUM(o.total_amount), 2) as revenue,
                       SUM(o.quantity) as units_sold
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.product_name
                ORDER BY revenue DESC
            """)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(
                    df, x="product_name", y="revenue",
                    title="Revenue by product",
                    color="revenue",
                    color_continuous_scale="Blues",
                    labels={"product_name": "Product", "revenue": "Revenue ($)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(
                    df, names="product_name", values="revenue",
                    title="Revenue share by product",
                    hole=0.4
                )
                st.plotly_chart(fig2, use_container_width=True)

        elif chart_type == "monthly":
            df = run_query("""
                SELECT strftime('%Y-%m', order_date) as month,
                       ROUND(SUM(total_amount), 2) as revenue,
                       COUNT(*) as orders
                FROM orders
                GROUP BY month ORDER BY month
            """)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.line(
                    df, x="month", y="revenue",
                    title="Monthly revenue trend",
                    markers=True,
                    labels={"month": "Month", "revenue": "Revenue ($)"}
                )
                fig.update_traces(line_color="#7F77DD", line_width=3)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.bar(
                    df, x="month", y="orders",
                    title="Monthly order count",
                    color="orders",
                    color_continuous_scale="Teal",
                    labels={"month": "Month", "orders": "Orders"}
                )
                st.plotly_chart(fig2, use_container_width=True)

        elif chart_type == "region":
            df = run_query("""
                SELECT c.region,
                       ROUND(SUM(o.total_amount), 2) as revenue,
                       COUNT(*) as orders
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.region ORDER BY revenue DESC
            """)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(
                    df, x="region", y="revenue",
                    title="Revenue by region",
                    color="region",
                    labels={"region": "Region", "revenue": "Revenue ($)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(
                    df, names="region", values="revenue",
                    title="Revenue share by region",
                    hole=0.4
                )
                st.plotly_chart(fig2, use_container_width=True)

        elif chart_type == "category":
            df = run_query("""
                SELECT p.category,
                       ROUND(SUM(o.total_amount), 2) as revenue,
                       SUM(o.quantity) as units_sold
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.category ORDER BY revenue DESC
            """)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(
                    df, x="category", y="revenue",
                    title="Revenue by category",
                    color="category",
                    labels={"category": "Category", "revenue": "Revenue ($)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(
                    df, names="category", values="units_sold",
                    title="Units sold by category",
                    hole=0.4
                )
                st.plotly_chart(fig2, use_container_width=True)

        elif chart_type == "customer":
            df = run_query("""
                SELECT c.customer_name,
                       ROUND(SUM(o.total_amount), 2) as revenue,
                       COUNT(*) as orders
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.customer_name ORDER BY revenue DESC
            """)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(
                    df, x="customer_name", y="revenue",
                    title="Revenue by customer",
                    color="revenue",
                    color_continuous_scale="Oranges",
                    labels={"customer_name": "Customer", "revenue": "Revenue ($)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.scatter(
                    df, x="orders", y="revenue",
                    text="customer_name",
                    title="Orders vs Revenue",
                    labels={"orders": "Number of orders", "revenue": "Revenue ($)"}
                )
                fig2.update_traces(textposition="top center", marker_size=12)
                st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard chart error: {str(e)}")


# ── Page header ───────────────────────────────────────────
st.title("Sales AI Agent")
st.caption("Ask anything about your sales data in plain English — no SQL needed.")

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Quick questions")
    questions = [
        "Show total sales for the last 5 months",
        "Which product had the highest sales?",
        "Show sales by region",
        "Which customer spent the most?",
        "Show monthly sales trend",
        "Show top 3 products by revenue",
        "Compare sales by category",
    ]
    for q in questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_q = q

    st.markdown("---")
    st.markdown("### Charts")
    if st.button("Revenue by product", use_container_width=True):
        st.session_state.show_chart = "product"
    if st.button("Monthly trend", use_container_width=True):
        st.session_state.show_chart = "monthly"
    if st.button("Sales by region", use_container_width=True):
        st.session_state.show_chart = "region"
    if st.button("Sales by category", use_container_width=True):
        st.session_state.show_chart = "category"
    if st.button("Customer spending", use_container_width=True):
        st.session_state.show_chart = "customer"

# ── KPI Metrics ───────────────────────────────────────────
try:
    df_kpi = run_query("""
        SELECT
            ROUND(SUM(total_amount), 2) as total_revenue,
            COUNT(*) as total_orders,
            ROUND(AVG(total_amount), 2) as avg_order,
            COUNT(DISTINCT customer_id) as total_customers
        FROM orders
    """)
    df_month = run_query("""
        SELECT ROUND(SUM(total_amount), 2) as this_month
        FROM orders
        WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
    """)
    df_last = run_query("""
        SELECT ROUND(SUM(total_amount), 2) as last_month
        FROM orders
        WHERE strftime('%Y-%m', order_date) =
              strftime('%Y-%m', date('now', '-1 month'))
    """)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Revenue", f"${df_kpi['total_revenue'][0]:,.0f}")
    with col2:
        st.metric("Total Orders", int(df_kpi['total_orders'][0]))
    with col3:
        st.metric("Avg Order", f"${df_kpi['avg_order'][0]:,.0f}")
    with col4:
        st.metric("Customers", int(df_kpi['total_customers'][0]))
    with col5:
        this_m = df_month['this_month'][0] or 0
        last_m = df_last['last_month'][0] or 0
        delta = round(this_m - last_m, 2)
        st.metric("This Month", f"${this_m:,.0f}",
                  delta=f"${delta:,.0f} vs last month")
except Exception:
    st.info("Loading metrics...")

st.divider()

# ── Dashboard charts ──────────────────────────────────────
if "show_chart" in st.session_state:
    show_dashboard_chart(st.session_state.show_chart)
    st.divider()

# ── Chat history ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart" in msg:
            st.plotly_chart(msg["chart"], use_container_width=True)

# ── Chat input ────────────────────────────────────────────
user_input = st.chat_input("Ask about your sales data...")

if "quick_q" in st.session_state:
    user_input = st.session_state.pop("quick_q")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analysing your data..."):
            try:
                answer = ask_agent(user_input)
                st.markdown(answer)

                fig = auto_chart(user_input)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "chart": fig
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")