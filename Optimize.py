import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

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
    st.session_state.page = 'Overall Performance'  # Default page

# ---------- FUNCTION TO CHANGE PAGE ----------
def change_page(page_name):
    st.session_state.page = page_name

# ---------- TOP NAVIGATION BUTTONS ----------
st.markdown("### 📁 Welcome To MBCS Optimize Tool")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📂 Overall Performance"):
        change_page("Overall Performance")

with col2:
    if st.button("💰 Influencer Performance"):
        change_page("Influencer Performance")

with col3:
    if st.button("📋 Summary Budget"):
        change_page("Summary Budget")

# ---------- PAGE 1:
# Initialize session state
# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Overall Performance"
if 'inputs' not in st.session_state:
    st.session_state.inputs = {'VIP': 0, 'Top': 0, 'Mid': 0, 'Macro': 0, 'Nano': 0}
if 'category' not in st.session_state:
    st.session_state.category = "F&B"

# ---------- PAGE 1: INPUT DATA ----------
if st.session_state.page == "Overall Performance":
    st.title("📊 Overall Performance")
    
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
sheet_url = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"

@st.cache_data  # Cache to speed up loading
def load_google_sheets(url):
    return pd.read_csv(url)

# Load the data
df = load_google_sheets(sheet_url)

# ---------- PAGE 2: SCENARIO BUDGET ----------
if st.session_state.page == "Influencer Performance":
    st.title("💰 Influencer Performance")

    # Show Data
    st.subheader("📋 Influencer Performance from Google Sheets")
    st.dataframe(df)  # Display the Google Sheets data

        # Show the data (for reference)
    st.subheader("📋 Budget Data from Google Sheets")
    st.dataframe(df)  # Display the full Google Sheets data

    # Create a drop-down list for multi-selecting KOL Names
    kol_names = df['KOL Name'].unique()  # Get unique KOL names from the column
    selected_kols = st.multiselect("Select KOL Names", options=kol_names)

    # Filter the data based on selected KOL Names
    if selected_kols:
        filtered_df = df[df['KOL Name'].isin(selected_kols)]

        # Show the filtered data: KOL, Comment, Share, Reach
        st.subheader("📊 KOL Data: Comment, Share, Reach")
        selected_data = filtered_df[['KOL Name', 'Comment', 'Share', 'Reach']]  # Extract relevant columns
        st.dataframe(selected_data)  # Display the filtered data
    else:
        st.warning("Please select at least one KOL.")

    # # Donut Chart
    # st.subheader("🍩 Budget Distribution")
    # donut_fig = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.4, title="Budget Breakdown")
    # st.plotly_chart(donut_fig, use_container_width=True)

    # # Line Chart
    # st.subheader("📈 Budget Over Time")
    # df_melted = df.melt(id_vars=df.columns[0], var_name="Category", value_name="Budget")
    
    # line_fig = px.line(df_melted, x=df.columns[0], y="Budget", color="Category", markers=True, title="Monthly Budget Trend")
    # st.plotly_chart(line_fig, use_container_width=True)


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