import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# Function to set black background with black font for login inputs
def set_black_background():
    # Set a solid black background and make the input text black
    bg_style = """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    .stTextInput input, .stTextArea textarea {
        color: black;
        background-color: white;
    }
    .stButton>button {
        color: black;
    }
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# If user is NOT logged in, show login page with black background
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    set_black_background()  # Set black background
    
    # Title with larger and bold text
    st.markdown("<h1 style='text-align: center; color: white;'>🔒 Welcome to MBCS</h1>", unsafe_allow_html=True)

    # Bold and white color for the input labels
    st.markdown("<h3 style='color: white; font-weight: bold;'>Username</h3>", unsafe_allow_html=True)
    st.text_input("", key="username")
    
    st.markdown("<h3 style='color: white; font-weight: bold;'>Password</h3>", unsafe_allow_html=True)
    st.text_input("", type="password", key="password")

    # Login button
    if st.button("Login"):
        if st.session_state.username == "mbcs" and st.session_state.password == "1234":
            st.session_state.authenticated = True
        else:
            st.error("❌ Incorrect username or password. Please try again.")
    
    st.stop()  # Stop execution if not logged in

# ---------- SESSION STATE FOR DATA SHARING ----------
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'VIP': 0,
        'Top': 0,
        'Mid': 0,
        'Macro': 0,
        'Nano': 0
    }

if 'page' not in st.session_state:
    st.session_state.page = 'Input Data'  # Default page

# ---------- FUNCTION TO CHANGE PAGE ----------
def change_page(page_name):
    st.session_state.page = page_name

# ---------- TOP NAVIGATION BUTTONS ----------
st.markdown("### 📁 Welcome To MBCS Optimize Tool")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📂 Input Data"):
        change_page("Input Data")

with col2:
    if st.button("💰 Scenario Budget"):
        change_page("Scenario Budget")

with col3:
    if st.button("📋 Summary Budget"):
        change_page("Summary Budget")

# ---------- PAGE 1:
# Initialize session state
# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Input Data"
if 'inputs' not in st.session_state:
    st.session_state.inputs = {'VIP': 0, 'Top': 0, 'Mid': 0, 'Macro': 0, 'Nano': 0}
if 'category' not in st.session_state:
    st.session_state.category = "F&B"

# ---------- PAGE 1: INPUT DATA ----------
if st.session_state.page == "Input Data":
    st.title("📊 Input Data")
    
    # Category selection dropdown
    category = st.selectbox("Select Category:", ["F&B", "Cosmetic"], index=(0 if st.session_state.category == "F&B" else 1))
    st.session_state.category = category
    
    # Get input values
    vip = st.session_state.inputs['VIP']
    top = st.session_state.inputs['Top']
    mid = st.session_state.inputs['Mid']
    macro = st.session_state.inputs['Macro']
    nano = st.session_state.inputs['Nano']
    
    # Define weights based on category
    if category == "F&B":
        impression_weights = {'VIP': 5, 'Top': 3, 'Mid': 2, 'Macro': 1, 'Nano': 0.5}
        view_weights = {'VIP': 3, 'Top': 2, 'Mid': 1, 'Macro': 0.5, 'Nano': 0.25}
        engagement_weights = {'VIP': 1, 'Top': 0.5, 'Mid': 0.25, 'Macro': 0.1, 'Nano': 0.005}
    else:  # Cosmetic
        impression_weights = {'VIP': 3, 'Top': 2, 'Mid': 1, 'Macro': 0.5, 'Nano': 0.25}
        view_weights = {'VIP': 1, 'Top': 0.75, 'Mid': 0.5, 'Macro': 0.25, 'Nano': 0.1}
        engagement_weights = {'VIP': 0.5, 'Top': 0.25, 'Mid': 0.1, 'Macro': 0.005, 'Nano': 0.001}
    
    # Calculate summary metrics
    total_sum = vip + top + mid + macro + nano
    total_impressions = sum(st.session_state.inputs[k] * v for k, v in impression_weights.items())
    total_views = sum(st.session_state.inputs[k] * v for k, v in view_weights.items())
    total_engagement = sum(st.session_state.inputs[k] * v for k, v in engagement_weights.items())
    
    # Summary metrics display
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; padding: 15px; background-color: #f0f2f6; 
                    color: black; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); text-align: center;">
            <div>
                <h4>📢 Total Impressions</h4>
                <h2 style="color:#2196F3;">{total_impressions:,.0f}</h2>
            </div>
            <div>
                <h4>👀 Total Views</h4>
                <h2 style="color:#FF9800;">{total_views:,.0f}</h2>
            </div>
            <div>
                <h4>💬 Total Engagement</h4>
                <h2 style="color:#E91E63;">{total_engagement:,.0f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout with input fields
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Enter Data")
        new_values = {}
        for category in ['VIP', 'Top', 'Mid', 'Macro', 'Nano']:
            cols = st.columns([3, 1])  # Adjusted column ratio for better alignment
            new_values[category] = cols[0].number_input(f"{category}", min_value=0, value=st.session_state.inputs[category], key=category)
            percentage = (new_values[category] / total_sum * 100) if total_sum > 0 else 0
            
            # HTML structure with label on top of the percentage box
            cols[1].markdown(f"""
                <div style='text-align:center; margin-bottom:5px; font-size:14px; color:#555;'>
                    %
                </div>
                <div style='display:flex; align-items:center; justify-content:center; height:40px; 
                            width:100%; border-radius:5px; border:1px solid #ddd; padding:5px; text-align:center; line-height: 35px;'>
                    {percentage:.2f}%
                </div>
            """, unsafe_allow_html=True)
        
        # Update session state on change
        if new_values != st.session_state.inputs:
            st.session_state.inputs = new_values
            st.rerun()

    # Right side: Total Budget Card
    with col2:
        st.subheader("💰 Total Budget")
        st.markdown(
            f"""
            <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center;
                        box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                <h3>💰 Budget</h3>
                <h1 style="color:#4CAF50;">{total_sum}</h1>
            </div>
            """, unsafe_allow_html=True
        )




# # ---------- PAGE 1: INPUT DATA ----------
# if st.session_state.page == "Input Data":
#     st.title("📊 Input Data")

#     # Layout with two columns
#     col1, col2 = st.columns([2, 1])  # Left column wider than the right

#     # ---------- LEFT SIDE: INPUT FIELDS ----------
#     with col1:
#         st.subheader("🎯 Enter Data")
#         vip = st.number_input("1.1 VIP", min_value=0, value=st.session_state.inputs['VIP'], key='vip')
#         top = st.number_input("1.2 Top", min_value=0, value=st.session_state.inputs['Top'], key='top')
#         mid = st.number_input("1.3 Mid", min_value=0, value=st.session_state.inputs['Mid'], key='mid')
#         macro = st.number_input("1.4 Macro", min_value=0, value=st.session_state.inputs['Macro'], key='macro')
#         nano = st.number_input("1.5 Nano", min_value=0, value=st.session_state.inputs['Nano'], key='nano')

#         # Submit Button
#         if st.button("Submit"):
#             st.session_state.inputs = {
#                 'VIP': vip,
#                 'Top': top,
#                 'Mid': mid,
#                 'Macro': macro,
#                 'Nano': nano
#             }
#             st.success("✅ Data Submitted Successfully!")

#     # ---------- RIGHT SIDE: SUMMARY CARD ----------
#     with col2:
#         st.subheader("📋 Summary")
#         total_sum = vip + top + mid + macro + nano

#         # Card-style display using markdown
#         st.markdown(
#             f"""
#             <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center;box-shadow:0 2px 5px rgba(0,0,0,0.1);">
#                 <h3>Total Budget</h3>
#                 <h1 style="color:#4CAF50;">{total_sum}</h1>
#             </div>
#             """, unsafe_allow_html=True
#         )

# ---------- PAGE 2: SCENARIO BUDGET ----------
elif st.session_state.page == "Scenario Budget":
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
elif st.session_state.page == "Summary Budget":
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