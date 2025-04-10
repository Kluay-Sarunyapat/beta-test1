import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import requests
import io
import time
from scipy.optimize import linprog


# Set Streamlit to wide layout
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .appview-container .main {
        max-width: 1100px !important; /* Adjust width as needed */
        margin: auto;
    }
    .block-container {
        max-width: 1100px !important; /* Adjust width as needed */
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to set black background with black font for login inputs
def set_black_background():
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

# List of valid usernames and passwords
valid_users = {
    "mbcs": "1234",
    "mbcs1": "5678",
    "admin": "adminpass"  # Add more users if needed
}

# If user is NOT logged in, show login page with black background
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    set_black_background()  # Set black background
    
    # Logo image (Google Drive direct link)
    logo_url = "https://i.postimg.cc/x1JFDk6P/Nest.webp"
    st.markdown(f"<div style='text-align: center;'><img src='{logo_url}' width='200'></div>", unsafe_allow_html=True)

    # Title with larger and bold text
    st.markdown("<h1 style='text-align: center; color: white;'>🔒 WELCOME TO NEST OPTIMIZED TOOL</h1>", unsafe_allow_html=True)

    # Bold and white color for the input labels
    st.markdown("<h3 style='color: white; font-weight: bold;'>Username</h3>", unsafe_allow_html=True)
    username = st.text_input("", key="username")
    
    st.markdown("<h3 style='color: white; font-weight: bold;'>Password</h3>", unsafe_allow_html=True)
    password = st.text_input("", type="password", key="password")

    # Login button
    if st.button("Login"):
        if username in valid_users and password == valid_users[username]:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Incorrect username or password. Please try again.")
    
    st.stop()  # Stop execution if not logged in

# After login, show main content
st.write("🎉 Welcome! You are now logged in.")

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
    st.session_state.page = 'Simulation Budget'  # Default page

# ---------- FUNCTION TO CHANGE PAGE ----------
def change_page(page_name):
    st.session_state.page = page_name

# ---------- TOP NAVIGATION BUTTONS ----------
st.markdown("### 📁 Welcome To MBCS Optimize Tool")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📂 Simulation Budget"):
        change_page("Simulation Budget")

with col2:
    if st.button("💰 Influencer Performance"):
        change_page("Influencer Performance")

with col3:
    if st.button("📋 Optimized Budget"):
        change_page("Optimized Budget")

with col4:
    if st.button("🤖 GEN AI"):
        change_page("GEN AI")

# ---------- PAGE 1:
# Initialize session state
# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Simulation Budget"
if 'inputs' not in st.session_state:
    st.session_state.inputs = {'VIP': 0, 'Top': 0, 'Mid': 0, 'Macro': 0, 'Nano': 0}
if 'category' not in st.session_state:
    st.session_state.category = "F&B"

# ---------- PAGE 1: INPUT DATA ----------
if st.session_state.page == "Simulation Budget":
    st.title("📊 Simulation Budget")
    
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



# ---------- PAGE 2: Influencer Performance ----------
# Google Sheets CSV direct link
sheet_url_raw = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"
sheet_url_off = "https://docs.google.com/spreadsheets/d/1Fst4_Ac4SwmY4WQ1S_rzXSgmrxDb3jvp/gviz/tq?tqx=out:csv"

@st.cache_data
def load_google_sheets(url):
    return pd.read_csv(url)

# Button to trigger refresh
if st.button('Refresh Data'):
    st.cache_data.clear()  # Clear cache when the button is pressed

# Load the data
df = load_google_sheets(sheet_url_raw)
df_coff = load_google_sheets(sheet_url_off)

# # Display the data
# st.write(df)


# # ---------- PAGE 2: Influencer Performance ----------
# # Google Sheets CSV direct link
# sheet_url_raw = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"
# sheet_url_off = "https://docs.google.com/spreadsheets/d/1Fst4_Ac4SwmY4WQ1S_rzXSgmrxDb3jvp/gviz/tq?tqx=out:csv"

# @st.cache_data
# def load_google_sheets(url):
#     return pd.read_csv(url)

# # Load the data
# df = load_google_sheets(sheet_url_raw)
# df_coff = load_google_sheets(sheet_url_off)

# ---------- PAGE 2: Influencer Performance ----------
# Google Sheets CSV direct link
sheet_url_raw = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"
sheet_url_off = "https://docs.google.com/spreadsheets/d/1Fst4_Ac4SwmY4WQ1S_rzXSgmrxDb3jvp/gviz/tq?tqx=out:csv"

@st.cache_data  # Cache to speed up loading
def load_google_sheets(url):
    return pd.read_csv(url)

# Load the data
df = load_google_sheets(sheet_url_raw)
df_coff = load_google_sheets(sheet_url_off)

# ---------- PAGE: INFLUENCER PERFORMANCE ----------
if st.session_state.page == "Influencer Performance":
    st.title("💰 Influencer Performance")

    # Show Data
    st.subheader("📋 Influencer Performance from Google Sheets")
    st.dataframe(df)  # Display the Google Sheets data

    # --- 1️⃣ Platform Selection and KOL Selection on Same Row ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🌍 Select Platform")
        platforms = df_coff['Platform'].unique()  # Get unique platforms
        selected_platform = st.selectbox("Select a Platform", options=platforms)

    with col2:
        st.subheader("🌍 Select KPIs")
        cost_per = df_coff['CPX'].unique()  # Get unique platforms
        selected_cost_per = st.selectbox("Select a Cost Per XXX", options=cost_per)
        

    with col3:
        st.subheader("🧑‍💼 Select KOL(s)")
        # Filter KOLs based on selected platform and cost per (CPX)
        filtered_kols_df_coff = df_coff[(df_coff['Platform'] == selected_platform) & 
                                        (df_coff['CPX'] == selected_cost_per)]  # Filter by both platform and CPX
        kol_names = filtered_kols_df_coff['KOL Name'].unique()  # Get unique KOL names
        selected_kols = st.multiselect("Select KOL Names", options=kol_names)

        # Input box for cost
        Budget = st.number_input("💰 Enter Budget", min_value=0.0, value=0.1, step=0.01)

    if selected_kols:  # Check if any KOLs are selected
        st.subheader("📊 Results")

        # Filter the data based on selected KOL names and platform
        selected_kol_data = filtered_kols_df_coff[filtered_kols_df_coff['KOL Name'].isin(selected_kols)]

        if not selected_kol_data.empty:
            # Ensure 'Value' is numeric and calculate the Budget / Value for each selected KOL using `.loc` to avoid SettingWithCopyWarning
            selected_kol_data['Value'] = pd.to_numeric(selected_kol_data['Value'], errors='coerce')  # Convert to numeric
            selected_kol_data['Budget / Value'] = Budget / selected_kol_data['Value']  # Calculate Budget / Value

            # Display results for each selected KOL
            for index, row in selected_kol_data.iterrows():
                st.write(f"KOL Name: {row['KOL Name']}")
                st.write(f"Platform: {row['Platform']}")
                st.write(f"CPX Type: {row['CPX']}")
                st.write(f"Budget: {Budget}")

                # Determine which calculation to display based on CPX type
                if row['CPX'] == 'CPR':
                    st.write(f"Calculated Value (Reach): {row['Budget / Value']:.2f}")  # Format to 2 decimal places
                elif row['CPX'] == 'CPI':
                    st.write(f"Calculated Value (Impression): {row['Budget / Value']:.2f}")
                elif row['CPX'] == 'CPE':
                    st.write(f"Calculated Value (Engagement): {row['Budget / Value']:.2f}")
                elif row['CPX'] == 'CPC':
                    st.write(f"Calculated Value (Click): {row['Budget / Value']:.2f}")
                elif row['CPX'] == 'CPV':
                    st.write(f"Calculated Value (View): {row['Budget / Value']:.2f}")
                else:
                    st.write(f"Calculated Value: {row['Budget / Value']:.2f}")  # Default case

                st.write("---")
        else:
            st.write("No data found for the selected KOL(s). Please check your selection.")
    else:
        st.write("No KOLs selected. Please select at least one KOL.")


# ---------- PAGE 3: SUMMARY BUDGET ----------
elif st.session_state.page == "Optimized Budget":
    st.title("📋 Optimized Budget")

    # # Random Data for Charts
    # random_df = pd.DataFrame({
    #     'Category': ['VIP', 'Top', 'Mid', 'Macro', 'Nano'],
    #     'Budget': np.random.randint(100, 500, 5)
    # })

    # # Chart 1: Bar Chart
    # st.subheader("📊 Random Budget Distribution")
    # bar_fig = px.bar(random_df, x='Category', y='Budget', color='Category', title="Random Bar Chart")
    # st.plotly_chart(bar_fig, use_container_width=True)

    # # Chart 2: Area Chart
    # st.subheader("🌄 Random Budget Over Time")
    # area_df = pd.DataFrame({
    #     'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    #     'Budget': np.random.randint(200, 600, 5)
    # })

    # area_fig = px.area(area_df, x='Month', y='Budget', title="Random Area Chart")
    # st.plotly_chart(area_fig, use_container_width=True)
    # Define KPI weights (different for F&B and Cosmetic)
    def get_weights(category):
        if category == "F&B":
            impression_weights = {'VIP': 5, 'Top': 3, 'Mid': 2, 'Macro': 1, 'Nano': 0.5}
            view_weights = {'VIP': 3, 'Top': 2, 'Mid': 1, 'Macro': 0.5, 'Nano': 0.25}
            engagement_weights = {'VIP': 1, 'Top': 0.5, 'Mid': 0.25, 'Macro': 0.1, 'Nano': 0.005}
        else:  # Cosmetic
            impression_weights = {'VIP': 3, 'Top': 2, 'Mid': 1, 'Macro': 0.5, 'Nano': 0.25}
            view_weights = {'VIP': 1, 'Top': 0.75, 'Mid': 0.5, 'Macro': 0.25, 'Nano': 0.1}
            engagement_weights = {'VIP': 0.5, 'Top': 0.25, 'Mid': 0.1, 'Macro': 0.005, 'Nano': 0.001}
        
        return impression_weights, view_weights, engagement_weights
    
    def optimize_budget(total_budget, min_alloc, max_alloc, priority='balanced', category="F&B"):
        tiers = ['VIP', 'Top', 'Mid', 'Macro', 'Nano']
        num_tiers = len(tiers)
        
        # Get KPI weights based on selected category
        impression_weights, view_weights, engagement_weights = get_weights(category)
        
        # Define KPI objective coefficients based on priority
        if priority == 'impressions':
            weights = [impression_weights[t] for t in tiers]
        elif priority == 'views':
            weights = [view_weights[t] for t in tiers]
        elif priority == 'engagement':
            weights = [engagement_weights[t] for t in tiers]
        else:
            weights = [(impression_weights[t] + view_weights[t] + engagement_weights[t]) / 3 for t in tiers]
        
        # Convert to negative for maximization
        c = -np.array(weights)
        
        # Constraints: Budget and min/max allocations
        A_eq = [np.ones(num_tiers)]
        b_eq = [total_budget]
        
        bounds = [(min_alloc[t], max_alloc[t]) for t in tiers]
        
        # Solve optimization
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            allocation = {tiers[i]: res.x[i] for i in range(num_tiers)}
            impressions = sum(res.x[i] * impression_weights[tiers[i]] for i in range(num_tiers))
            views = sum(res.x[i] * view_weights[tiers[i]] for i in range(num_tiers))
            engagement = sum(res.x[i] * engagement_weights[tiers[i]] for i in range(num_tiers))
            total_kpi = impressions + views + engagement
            return allocation, impressions, views, engagement, total_kpi
        else:
            return None, None, None, None, None
    
    # Streamlit UI
    st.title("📊 Budget Optimization Tool")
    
    # Category selection
    category = st.selectbox("Select Category:", ["F&B", "Cosmetic"])
    
    # Total Budget input
    total_budget = st.number_input("Enter Total Budget:", min_value=0, value=10000, step=100)
    
    # Min/Max Allocation inputs
    min_alloc = {}
    max_alloc = {}
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Minimum Allocation")
        for tier in ['VIP', 'Top', 'Mid', 'Macro', 'Nano']:
            min_alloc[tier] = st.number_input(f"Min {tier}", min_value=0, value=0)
    
    with col2:
        st.subheader("Maximum Allocation")
        for tier in ['VIP', 'Top', 'Mid', 'Macro', 'Nano']:
            max_alloc[tier] = st.number_input(f"Max {tier}", min_value=0, value=total_budget)
    
    # Priority selection for optimization
    priority = st.selectbox("Select Optimization Priority:", ["balanced", "impressions", "views", "engagement"])
    
    # Optimization button
    if st.button("Optimize Budget"):
        allocation, impressions, views, engagement, total_kpi = optimize_budget(total_budget, min_alloc, max_alloc, priority, category)
        
        if allocation:
            st.success("✅ Optimization Successful!")
            st.json(allocation)
            
            st.subheader("📊 KPI Breakdown")
            st.write(f"Impressions: {impressions:,.2f}")
            st.write(f"Views: {views:,.2f}")
            st.write(f"Engagement: {engagement:,.2f}")
            st.write(f"💰 **Total KPI (Impressions + Views + Engagement)**: {total_kpi:,.2f}")
        else:
            st.error("❌ Optimization failed. Check constraints.")

#Page4
if st.session_state.page == "GEN AI":
    st.title(" COMMING SOON...")
