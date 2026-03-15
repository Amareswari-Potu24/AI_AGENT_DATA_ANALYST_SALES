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

st.title("Sales AI Agent")
st.caption("Ask anything about your sales data in plain English — no SQL needed.")

with st.sidebar:
    st.markdown("### Quick questions")
    questions = [
        "Show total sales for the last 5 months",
        "Which product had the highest sales?",
        "Show sales by region",
        "Which customer spent the most?",
        "Show monthly sales trend",
    ]
    for q in questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_q = q

try:
    df_metrics = run_query("""
        SELECT 
            SUM(total_amount) as total_revenue,
            COUNT(*) as total_orders,
            AVG(total_amount) as avg_order,
            COUNT(DISTINCT customer_id) as customers
        FROM orders
    """)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${df_metrics['total_revenue'][0]:,.0f}")
    with col2:
        st.metric("Total Orders", int(df_metrics['total_orders'][0]))
    with col3:
        st.metric("Avg Order", f"${df_metrics['avg_order'][0]:,.0f}")
    with col4:
        st.metric("Customers", int(df_metrics['customers'][0]))
except Exception:
    st.info("Loading metrics...")

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                fig = generate_chart(user_input)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

def generate_chart(question: str):
    q = question.lower()
    try:
        if any(w in q for w in ["month", "trend"]):
            df = run_query("""
                SELECT strftime('%Y-%m', order_date) as month,
                       SUM(total_amount) as revenue
                FROM orders
                GROUP BY month ORDER BY month
            """)
            if df.empty: return None
            return px.line(df, x="month", y="revenue",
                          title="Monthly revenue trend", markers=True)

        elif any(w in q for w in ["product", "top", "highest"]):
            df = run_query("""
                SELECT p.product_name, SUM(o.total_amount) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.product_name
                ORDER BY revenue DESC
            """)
            if df.empty: return None
            return px.bar(df, x="product_name", y="revenue",
                         title="Revenue by product")

        elif any(w in q for w in ["region", "area"]):
            df = run_query("""
                SELECT c.region, SUM(o.total_amount) as revenue
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.region ORDER BY revenue DESC
            """)
            if df.empty: return None
            return px.pie(df, names="region", values="revenue",
                         title="Revenue by region")

        elif any(w in q for w in ["customer", "who"]):
            df = run_query("""
                SELECT c.customer_name, SUM(o.total_amount) as revenue
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                GROUP BY c.customer_name ORDER BY revenue DESC
            """)
            if df.empty: return None
            return px.bar(df, x="customer_name", y="revenue",
                         title="Revenue by customer")
    except Exception:
        return None
    return None