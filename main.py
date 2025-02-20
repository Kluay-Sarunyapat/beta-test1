import streamlit as st
import pandas as pd
import plotly.express as px

# Sample Data
data = {
    'Channel': ['Brandtv', 'Bvod', 'Bvod', 'Display', 'Drtv', 'Fb', 'Fb', 'Fb', 'Olv', 'Olv', 'Ppc', 'Radio', 'Twitter'],
    'Objective': ['Awareness', 'Awareness', 'Conversion', 'Conversion', 'Conversion', 'Awareness', 'Conversion', 'Preference', 'Awareness', 'Preference', 'Conversion', 'Awareness', 'Preference'],
    'Tactic': ['Prospect'] * 13,
    'Plan Budget': [98179.77, 11571.31, 457.49, 4841.28, 12977.48, 1320.65, 353.52, 3144.15, 1908.98, 6427.89, 28393.18, 6238.01, 273.25],
    'Optimized Budget': [98179.77, 11571.31, 457.49, 1639.48, 12977.48, 1281.07, 2129.82, 2447.29, 3626.60, 6504.21, 27447.50, 6238.01, 2396.94],
    'CPL': [386.21, 133.27, 105.01, 162.29, 222.91, 133.02, 108.59, 128.15, 118.32, 112.93, 111.63, 299.09, 113.82],
    'mCPL': [864.82, 173.16, 105.01, 399.45, 489.77, 133.02, 108.59, 156.50, 118.32, 149.10, 148.17, 638.85, 113.82],
    'Leads': [254.21, 86.83, 4.36, 29.83, 58.22, 9.93, 3.26, 26.64, 16.13, 56.92, 259.19, 20.86, 2.4]
}
df = pd.DataFrame(data)

# Sidebar Filters
st.sidebar.title("Performance Planning")
client = st.sidebar.selectbox("Client", ["DEMO"])
market = st.sidebar.selectbox("Market", ["UK"])
kpi = st.sidebar.selectbox("KPI", ["Leads"])
model = st.sidebar.selectbox("Model", ["03_02"])
planning_period = st.sidebar.date_input("Planning Period", [])

# KPI Metrics
st.title("Performance Planning")
st.metric("Total Budget", "$176,897")
st.metric("MRI", "83.28%")
st.metric("Leads", "845")
st.metric("CPL", "$209.43")

# Toggle Switch
custom_plan = st.toggle("Custom Plan", value=True)

# Editable Table
st.subheader("Plan Details")
edited_df = st.data_editor(df, num_rows="dynamic")

# Scatter Plot
st.subheader("Planning Insights")
fig = px.scatter(
    df, x='Optimized Budget', y='Leads', text='Channel',
    color='Objective', size='Plan Budget',
    labels={'Optimized Budget': 'Planned Spend', 'Leads': 'Expected Leads'}
)
st.plotly_chart(fig)

# Expandable Insights
with st.expander("Response Curves"):
    st.write("Response curve data here.")

with st.expander("Share of Effect (Based on Custom Plan)"):
    st.write("Share of effect data here.")

with st.expander("Seasonality"):
    st.write("Seasonality insights here.")

with st.expander("Audience Insight"):
    st.write("Audience insights here.")
