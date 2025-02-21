import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- SESSION STATE FOR DATA SHARING ----------
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'VIP': 0,
        'Top': 0,
        'Mid': 0,
        'Macro': 0,
        'Nano': 0
    }

# ---------- SIDEBAR NAVIGATION ----------
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["Input Data", "Scenario Budget", "Summary Budget"])

# ---------- PAGE 1: INPUT DATA ----------
if page == "Input Data":
    st.title("📊 Input Data")

    # Input Fields
    vip = st.number_input("1.1 VIP", min_value=0, value=0)
    top = st.number_input("1.2 Top", min_value=0, value=0)
    mid = st.number_input("1.3 Mid", min_value=0, value=0)
    macro = st.number_input("1.4 Macro", min_value=0, value=0)
    nano = st.number_input("1.5 Nano", min_value=0, value=0)

    # Submit Button
    if st.button("Submit"):
        st.session_state.inputs = {
            'VIP': vip,
            'Top': top,
            'Mid': mid,
            'Macro': macro,
            'Nano': nano
        }
        st.success("✅ Data Submitted Successfully!")

# ---------- PAGE 2: SCENARIO BUDGET ----------
elif page == "Scenario Budget":
    st.title("💰 Scenario Budget")

    # Prepare Data
    input_data = st.session_state.inputs
    df = pd.DataFrame({
        'Category': list(input_data.keys()),
        'Value': list(input_data.values())
    })

    # Donut Chart
    st.subheader("🍩 Budget Distribution")
    donut_fig = px.pie(df, names='Category', values='Value', hole=0.4, title="Budget Breakdown")
    st.plotly_chart(donut_fig, use_container_width=True)

    # Line Chart
    st.subheader("📈 Budget Over Time")
    time_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'VIP': np.random.randint(50, 200, 5),
        'Top': np.random.randint(50, 200, 5),
        'Mid': np.random.randint(50, 200, 5),
        'Macro': np.random.randint(50, 200, 5),
        'Nano': np.random.randint(50, 200, 5)
    })
    time_df = time_df.melt(id_vars='Month', var_name='Category', value_name='Budget')

    line_fig = px.line(time_df, x='Month', y='Budget', color='Category', markers=True, title="Monthly Budget Trend")
    st.plotly_chart(line_fig, use_container_width=True)

# ---------- PAGE 3: SUMMARY BUDGET ----------
elif page == "Summary Budget":
    st.title("📋 Summary Budget")

    # Random Data for Charts
    random_df = pd.DataFrame({
        'Category': ['VIP', 'Top', 'Mid', 'Macro', 'Nano'],
        'Budget': np.random.randint(100, 500, 5)
    })

    # Chart 1: Bar Chart
    st.subheader("📊 Random Budget Distribution")
    bar_fig = px.bar(random_df, x='Category', y='Budget', color='Category', title="Random Bar Chart")
    st.plotly_chart(bar_fig, use_container_width=True)

    # Chart 2: Area Chart
    st.subheader("🌄 Random Budget Over Time")
    area_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Budget': np.random.randint(200, 600, 5)
    })

    area_fig = px.area(area_df, x='Month', y='Budget', title="Random Area Chart")
    st.plotly_chart(area_fig, use_container_width=True)

# ---------- END OF CODE ----------
