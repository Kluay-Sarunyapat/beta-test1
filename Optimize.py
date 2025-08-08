import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import requests
import io
import time
from scipy.optimize import linprog
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary
import altair as alt


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
    # logo_url = "https://i.postimg.cc/x1JFDk6P/Nest.webp"
    logo_url = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
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

#function to add logo
def show_logo(centered=True, width=200):
    logo_url = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
    if centered:
        st.markdown(f"<div style='text-align: center;'><img src='{logo_url}' width='{width}'></div>", unsafe_allow_html=True)
    else:
        st.image(logo_url, width=width)

# After login, show main content
show_logo(centered=True, width=150)
st.write("🎉 Welcome! You are now logged in.")

# ---------- SESSION STATE FOR DATA SHARING ----------
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'VIP': 0,
        'Mega': 0,
        'Macro': 0,
        'Mid': 0,
        'Micro': 0,
        'Nano': 0
    }

if 'page' not in st.session_state:
    st.session_state.page = 'Simulation Budget'  # Default page

# ---------- FUNCTION TO CHANGE PAGE ----------
def change_page(page_name):
    st.session_state.page = page_name

st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
        border-radius: 8px;
        background-color: #000000;
        color: white;
        border: none;
        transition: background-color 0.3s, color 0.3s;
        white-space: nowrap;  /* Prevents wrapping */
    }

    .stButton>button:hover {
        background-color: #333333;
        color: #ffffff;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- TOP NAVIGATION BUTTONS ----------
st.markdown("### 📁 Welcome To MBCS Optimize Tool")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Equal column widths

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

with col5:
    if st.button("📊 Dashboard"):
        change_page("Dashboard")

st.write(f"Current Page: {st.session_state.page}")


# ---------- FUNCTION: Load Weights from Google Sheet CSV ----------
@st.cache_data
def load_weights(csv_url):
    df = pd.read_csv(csv_url)
    return df

# Load weights from the published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/1CG19lrXCDYLeyPihaq4xwuPSw86oQUNB/export?format=csv"
weights_df = load_weights(csv_url)

# ---------- PAGE 1: Initialize session state ----------
# if 'page' not in st.session_state:
#     st.session_state.page = "Simulation Budget"
# if 'inputs' not in st.session_state:
#     st.session_state.inputs = {'VIP': 0, 'Mega': 0, 'Macro':0,'Mid': 0, 'Micro': 0, 'Nano': 0}
# if 'category' not in st.session_state:
#     st.session_state.category = weights_df['Category'].unique()[0]  # default first category

# # ---------- PAGE 1: INPUT DATA ----------
# if st.session_state.page == "Simulation Budget":
#     st.title("📊 Simulation Budget")

#     # Safe initialization of category in session state
#     available_categories = sorted(weights_df['Category'].unique())
#     if 'category' not in st.session_state or st.session_state.category not in available_categories:
#         st.session_state.category = available_categories[0]  # default to first valid category

#     # Category dropdown
#     category = st.selectbox("Select Category:", available_categories, index=available_categories.index(st.session_state.category))
#     st.session_state.category = category

#     # Get input values from session state
#     vip = st.session_state.inputs['VIP']
#     mega = st.session_state.inputs['Mega']
#     macro = st.session_state.inputs['Macro']
#     mid = st.session_state.inputs['Mid']
#     micro = st.session_state.inputs['Micro']
#     nano = st.session_state.inputs['Nano']

#     # Get weights from dataframe
#     def get_weights(kpi):
#         filtered = weights_df[(weights_df['Category'] == category) & (weights_df['KPI'] == kpi)]
#         return {row['Tier']: row['Weights'] for _, row in filtered.iterrows()}

#     impression_weights = get_weights("Impression")
#     view_weights = get_weights("View")
#     engagement_weights = get_weights("Engagement")

#     # Total budget
#     total_sum = vip + mega + macro + mid + micro + nano

#     # KPI calculations
#     total_impressions = sum(st.session_state.inputs[k] * impression_weights.get(k, 0) for k in st.session_state.inputs)
#     total_views = sum(st.session_state.inputs[k] * view_weights.get(k, 0) for k in st.session_state.inputs)
#     total_engagement = sum(st.session_state.inputs[k] * engagement_weights.get(k, 0) for k in st.session_state.inputs)

#     # Display summary metrics
#     st.markdown(
#         f"""
#         <div style="display: flex; justify-content: space-around; padding: 15px; background-color: #f0f2f6; 
#                     color: black; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); text-align: center;">
#             <div>
#                 <h4>📢 Total Impressions</h4>
#                 <h2 style="color:#2196F3;">{total_impressions:,.0f}</h2>
#             </div>
#             <div>
#                 <h4>👀 Total Views</h4>
#                 <h2 style="color:#FF9800;">{total_views:,.0f}</h2>
#             </div>
#             <div>
#                 <h4>💬 Total Engagement</h4>
#                 <h2 style="color:#E91E63;">{total_engagement:,.0f}</h2>
#             </div>
#         </div>
#         """, unsafe_allow_html=True
#     )

#     # Spacer
#     st.markdown("<br>", unsafe_allow_html=True)

#     # Layout with input fields
#     col1, col2 = st.columns([2, 1])

#     with col1:
#         st.subheader("🎯 Enter Data")
#         new_values = {}
#         for category_tier in ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']:
#             cols = st.columns([3, 1])
#             new_values[category_tier] = cols[0].number_input(
#                 f"{category_tier}", min_value=0, value=st.session_state.inputs[category_tier], key=category_tier
#             )
#             percentage = (new_values[category_tier] / total_sum * 100) if total_sum > 0 else 0
#             cols[1].markdown(f"""
#                 <div style='text-align:center; margin-bottom:5px; font-size:14px; color:#555;'>%</div>
#                 <div style='display:flex; align-items:center; justify-content:center; height:40px; 
#                             width:100%; border-radius:5px; border:1px solid #ddd; padding:5px; text-align:center; line-height: 35px;'>
#                     {percentage:.2f}%
#                 </div>
#             """, unsafe_allow_html=True)

#         # Update session state if user input changes
#         if new_values != st.session_state.inputs:
#             st.session_state.inputs = new_values
#             st.rerun()

#     with col2:
#         st.subheader("💰 Total Budget")
#         st.markdown(
#             f"""
#             <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center;
#                         box-shadow:0 2px 5px rgba(0,0,0,0.1);">
#                 <h3>💰 Budget</h3>
#                 <h1 style="color:#4CAF50;">{total_sum}</h1>
#             </div>
#             """, unsafe_allow_html=True
#         )

#testNew
# --- Initial Session State ---
if st.session_state.page == "Simulation Budget":
    st.title("📊 Simulation Budget")
    if 'inputs_a' not in st.session_state:
        st.session_state.inputs_a = dict(VIP=0, Mega=0, Macro=0, Mid=0, Micro=0, Nano=0)
    if 'inputs_b' not in st.session_state:
        st.session_state.inputs_b = dict(VIP=0, Mega=0, Macro=0, Mid=0, Micro=0, Nano=0)
    
    available_categories = sorted(weights_df['Category'].unique())
    if 'category_a' not in st.session_state:
        st.session_state.category_a = available_categories[0]
    if 'category_b' not in st.session_state:
        st.session_state.category_b = available_categories[0]
    
    st.title("📊 Budget Simulation Comparison")
    
    col_input_a, col_input_b = st.columns(2)
    
    def get_weights(category, kpi):
        filtered = weights_df[(weights_df['Category'] == category) & (weights_df['KPI'] == kpi)]
        return {row['Tier']: row['Weights'] for _, row in filtered.iterrows()}
    
    def colored_percentage(p):
        if p >= 40:
            return f"<span style='color:#1E90FF;font-weight:bold;'>{p:.1f}%</span>"
        elif p >= 20:
            return f"<span style='color:#FF9800;font-weight:bold;'>{p:.1f}%</span>"
        elif p > 0:
            return f"<span style='color:#009688;'>{p:.1f}%</span>"
        else:
            return "<span style='color:#aaa;'>0.0%</span>"
    
    with col_input_a:
        st.subheader("Simulation A")
        st.session_state.category_a = st.selectbox("Simulation A - Category:", available_categories, key="cat_a", index=available_categories.index(st.session_state.category_a))
        new_inputs_a = {}
        for t in st.session_state.inputs_a:
            total_a = sum(new_inputs_a.values()) if new_inputs_a else sum(st.session_state.inputs_a.values())
            cols = st.columns([3, 2])
            val = cols[0].number_input(f"{t}", min_value=0, value=st.session_state.inputs_a[t], key=f"a_{t}")
            new_inputs_a[t] = val
            total_a_new = sum(new_inputs_a.values())
            percent = (val / total_a_new) * 100 if total_a_new > 0 else 0
            cols[1].markdown(colored_percentage(percent), unsafe_allow_html=True)
        st.session_state.inputs_a = new_inputs_a
        total_a_final = sum(new_inputs_a.values())
        st.markdown(
            f"""
            <div style="background-color:#e0f7fa;padding:15px 0 15px 0;border-radius:12px;text-align:center;box-shadow:0 2px 5px #0288d180;">
                <div style="font-size:2.3rem;font-weight:bold;color:#0277bd;">{total_a_final:,}</div>
                <div style="font-size:1.2rem;">💰 Total Budget A</div>
            </div>
            """, unsafe_allow_html=True
        )
    
    with col_input_b:
        st.subheader("Simulation B")
        st.session_state.category_b = st.selectbox("Simulation B - Category:", available_categories, key="cat_b", index=available_categories.index(st.session_state.category_b))
        new_inputs_b = {}
        for t in st.session_state.inputs_b:
            total_b = sum(new_inputs_b.values()) if new_inputs_b else sum(st.session_state.inputs_b.values())
            cols = st.columns([3, 2])
            val = cols[0].number_input(f"{t}", min_value=0, value=st.session_state.inputs_b[t], key=f"b_{t}")
            new_inputs_b[t] = val
            total_b_new = sum(new_inputs_b.values())
            percent = (val / total_b_new) * 100 if total_b_new > 0 else 0
            cols[1].markdown(colored_percentage(percent), unsafe_allow_html=True)
        st.session_state.inputs_b = new_inputs_b
        total_b_final = sum(new_inputs_b.values())
        st.markdown(
            f"""
            <div style="background-color:#f3e5f5;padding:15px 0 15px 0;border-radius:12px;text-align:center;box-shadow:0 2px 5px #a26ad1;">
                <div style="font-size:2.3rem;font-weight:bold;color:#8e24aa;">{total_b_final:,}</div>
                <div style="font-size:1.2rem;">💰 Total Budget B</div>
            </div>
            """, unsafe_allow_html=True
        )
    
    def calc_metrics(inputs, category):
        impression_weights = get_weights(category, "Impression")
        view_weights = get_weights(category, "View")
        engagement_weights = get_weights(category, "Engagement")
        total_impressions = sum(inputs.get(k,0) * impression_weights.get(k, 0) for k in inputs)
        total_views = sum(inputs.get(k,0) * view_weights.get(k, 0) for k in inputs)
        total_engagement = sum(inputs.get(k,0) * engagement_weights.get(k, 0) for k in inputs)
        return total_impressions, total_views, total_engagement
    
    imp_a, view_a, eng_a = calc_metrics(st.session_state.inputs_a, st.session_state.category_a)
    imp_b, view_b, eng_b = calc_metrics(st.session_state.inputs_b, st.session_state.category_b)
    budget_a = sum(st.session_state.inputs_a.values())
    budget_b = sum(st.session_state.inputs_b.values())
    
    def highlight(a, b):
        if a > b:
            return (f"<span style='color:#388e3c;font-weight:bold;font-size:1.25em'>{a:,.0f}</span>",
                    f"<span style='color:#aaa;font-size:1.08em'>{b:,.0f}</span>")
        elif b > a:
            return (f"<span style='color:#aaa;font-size:1.08em'>{a:,.0f}</span>",
                    f"<span style='color:#388e3c;font-weight:bold;font-size:1.25em'>{b:,.0f}</span>")
        else:  # tie
            return (f"<span style='color:#1e88e5;font-weight:bold;font-size:1.2em'>{a:,.0f}</span>",
                    f"<span style='color:#1e88e5;font-weight:bold;font-size:1.2em'>{b:,.0f}</span>")
    
    imp_a_html, imp_b_html = highlight(imp_a, imp_b)
    view_a_html, view_b_html = highlight(view_a, view_b)
    eng_a_html, eng_b_html = highlight(eng_a, eng_b)
    budget_a_html, budget_b_html = highlight(budget_a, budget_b)
    
    st.markdown("---")
    st.subheader("📈 Simulation Results Comparison")
    
    st.markdown(
        f"""
        <table style="width:75%;margin:auto;border-collapse:collapse;font-size:1.17em;">
            <tr style="background-color:#f0f2f6;">
                <th style="width:28%"></th>
                <th style="color:#0277bd;">Simulation A</th>
                <th style="color:#8e24aa;">Simulation B</th>
            </tr>
            <tr>
                <td style="font-weight:bold">Category</td>
                <td>{st.session_state.category_a}</td>
                <td>{st.session_state.category_b}</td>
            </tr>
            <tr>
                <td style="font-weight:bold">Budget</td>
                <td>{budget_a_html}</td>
                <td>{budget_b_html}</td>
            </tr>
            <tr>
                <td style="font-weight:bold">Impressions</td>
                <td>{imp_a_html}</td>
                <td>{imp_b_html}</td>
            </tr>
            <tr>
                <td style="font-weight:bold">Views</td>
                <td>{view_a_html}</td>
                <td>{view_b_html}</td>
            </tr>
            <tr>
                <td style="font-weight:bold">Engagements</td>
                <td>{eng_a_html}</td>
                <td>{eng_b_html}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True
    )



# ---------- PAGE 2: Influencer Performance ----------
if st.session_state.page == "Influencer Performance":

    # ---------- GOOGLE SHEETS ----------
    sheet_url_raw = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"
    sheet_url_off = "https://docs.google.com/spreadsheets/d/1Fst4_Ac4SwmY4WQ1S_rzXSgmrxDb3jvp/gviz/tq?tqx=out:csv"
    sheet_url_full = "https://docs.google.com/spreadsheets/d/1f7x4teD3iBeFfhmpObHqcj8wl_DkipLwa_JxAO5sYp8/gviz/tq?tqx=out:csv"

    @st.cache_data
    def load_google_sheets(url):
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    if st.button('🔄 Refresh Data'):
        st.cache_data.clear()

    df = load_google_sheets(sheet_url_raw)
    df_coff = load_google_sheets(sheet_url_off)
    df_full = load_google_sheets(sheet_url_full)

    st.title("💰 Influencer Performance")

    st.write("🧾 Available columns:", df_full.columns.tolist())

    st.subheader("📋 Influencer Data from Google Sheets")
    st.dataframe(df_full)

    # --- Tier selection with exclusive 'All' ---
    all_tiers = ['All', 'VIP', 'Mega', 'Mid', 'Macro', 'Micro', 'Nano']

    if 'tier_selection' not in st.session_state:
        st.session_state.tier_selection = ['All']

    def update_tiers():
        selected = st.session_state['tier_multiselect']
        if 'All' in selected and len(selected) > 1:
            st.session_state.tier_selection = ['All']
        elif 'All' in selected and len(selected) == 1:
            st.session_state.tier_selection = ['All']
        else:
            if 'All' in selected:
                selected.remove('All')
            st.session_state.tier_selection = selected

    tier_selection = st.multiselect(
        "🏷️ Tier Selection",
        options=all_tiers,
        default=st.session_state.tier_selection,
        key='tier_multiselect',
        on_change=update_tiers
    )

    # Filter tiers for selection function
    if 'All' in st.session_state.tier_selection:
        filtered_tiers = None  # means no filter on tiers
    else:
        filtered_tiers = [tier.lower() for tier in st.session_state.tier_selection]

    def select_kols(df, budget, num_kols, kpi='total_impression', allowed_tiers=None):
        df = df.copy()

        # Note: Your columns are 'cost', 'impression', 'engagement', 'view' — adjust accordingly
        cost_col = 'cost'
        kpi_col = kpi  # e.g., 'total_impression' doesn't exist, map to correct columns
        # Map user KPI to actual column names
        kpi_map = {
            'total_impression': 'impression',
            'total_engagement': 'engagement',
            'total_view': 'view',
        }
        if kpi in kpi_map:
            kpi_col = kpi_map[kpi]

        # Remove rows without valid cost or KPI
        df = df[df[cost_col].notna() & (df[cost_col] > 0)]
        df = df[df[kpi_col].notna()]

        # Filter tiers if any specified
        if allowed_tiers is not None:
            df = df[df['tier'].str.lower().isin(allowed_tiers)]

        # Calculate score = KPI per cost
        df['score'] = df[kpi_col] / df[cost_col]

        df = df.sort_values(by='score', ascending=False)

        selected = []
        total_cost = 0

        for _, row in df.iterrows():
            if len(selected) >= num_kols:
                break
            if total_cost + row[cost_col] <= budget:
                selected.append(row)
                total_cost += row[cost_col]

        selected_df = pd.DataFrame(selected)

        if not selected_df.empty:
            summary = {
                'kol_name': 'TOTAL',
                'platform': '',
                'cost': selected_df[cost_col].sum(),
                'impression': selected_df['impression'].sum(),
                'engagement': selected_df['engagement'].sum(),
                'view': selected_df['view'].sum(),
                'followers': '',
                'tier': '',
                'score': ''
            }
            selected_df = pd.concat([selected_df, pd.DataFrame([summary])], ignore_index=True)

        return selected_df

        st.title("🎯 KOL Selection Optimizer")
    
        budget = st.number_input("💰 Total Budget (THB)", min_value=0, value=250000, step=1000)
        num_kols = st.number_input("🔢 Number of KOLs", min_value=1, value=5, step=1)
        kpi_option = st.selectbox("📊 KPI Focus", options=['total_impression', 'total_engagement', 'total_view'])
    
        if st.button("🚀 Run Selection"):
            result_df = select_kols(df_full, budget, num_kols, kpi=kpi_option, allowed_tiers=filtered_tiers)
            st.success("✅ KOL selection complete!")
            st.dataframe(result_df)
    
        with st.expander("🔍 Show Raw Data"):
            st.dataframe(df_full)
    
        ##Add New
        def optimize_kols_lp(df, budget, num_kols, kpi='impression', allowed_tiers=None):
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary
            import pandas as pd
        
            df = df.copy()
        
            # Clean input
            df = df[df['cost'].notna() & (df['cost'] > 0)]
            df = df[df[kpi].notna()]
        
            # Tier filter if applicable
            if allowed_tiers:
                df = df[df['tier'].str.lower().isin(allowed_tiers)]
        
            df = df.reset_index(drop=True)
        
            # Limit to 100 rows to keep solver fast
            if len(df) > 100:
                df = df.nlargest(100, kpi)
        
            # Define LP problem
            prob = LpProblem("KOL_Selection", LpMaximize)
            x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(len(df))]
        
            # Objective: maximize KPI
            prob += lpSum(df.loc[i, kpi] * x[i] for i in range(len(df)))
        
            # Constraints
            prob += lpSum(df.loc[i, 'cost'] * x[i] for i in range(len(df))) <= budget
            prob += lpSum(x[i] for i in range(len(df))) <= num_kols
        
            # Solve
            prob.solve()
        
            selected_rows = []
            for i in range(len(df)):
                if x[i].varValue == 1:
                    selected_rows.append(df.loc[i])
        
            result_df = pd.DataFrame(selected_rows)
        
            if not result_df.empty:
                summary = {
                    'kol_name': 'TOTAL',
                    'platform': '',
                    'cost': result_df["cost"].sum(),
                    'impression': result_df["impression"].sum(),
                    'engagement': result_df["engagement"].sum(),
                    'view': result_df["view"].sum(),
                    'followers': '',
                    'tier': '',
                    'score': ''
                }
                result_df = pd.concat([result_df, pd.DataFrame([summary])], ignore_index=True)
        
            return result_df

    
    st.title("🎯 KOL Selection Optimizer")
    
    selection_mode = st.radio("🔀 Optimization Method", ["Greedy", "Linear Programming"])
    
    budget = st.number_input("💰 Total Budget (THB)", min_value=0, value=250000, step=1000)
    num_kols = st.number_input("🔢 Number of KOLs", min_value=1, value=5, step=1)
    kpi_option = st.selectbox("📊 KPI Focus", options=['total_impression', 'total_engagement', 'total_view'])
    
    kpi_map = {
        'total_impression': 'impression',
        'total_engagement': 'engagement',
        'total_view': 'view',
    }
    kpi_col = kpi_map[kpi_option]
    
    if st.button("🚀 Run Optimization"):
        if selection_mode == "Greedy":
            result_df = select_kols(df_full, budget, num_kols, kpi=kpi_option, allowed_tiers=filtered_tiers)
        elif selection_mode == "Linear Programming":
            result_df = optimize_kols_lp(df_full, budget, num_kols, kpi=kpi_col, allowed_tiers=filtered_tiers)
    
        if not result_df.empty:
            st.success("✅ Optimization complete!")
            st.dataframe(result_df)
        else:
            st.warning("⚠️ No KOLs selected based on criteria.")
    
    # # --- 1️⃣ Platform Selection and KOL Selection on Same Row ---
    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     st.subheader("🌍 Select Platform")
    #     platforms = df_coff['Platform'].unique()  # Get unique platforms
    #     selected_platform = st.selectbox("Select a Platform", options=platforms)

    # with col2:
    #     st.subheader("🌍 Select KPIs")
    #     cost_per = df_coff['CPX'].unique()  # Get unique platforms
    #     selected_cost_per = st.selectbox("Select a Cost Per XXX", options=cost_per)
        

    # with col3:
    #     st.subheader("🧑‍💼 Select KOL(s)")
    #     # Filter KOLs based on selected platform and cost per (CPX)
    #     filtered_kols_df_coff = df_coff[(df_coff['Platform'] == selected_platform) & 
    #                                     (df_coff['CPX'] == selected_cost_per)]  # Filter by both platform and CPX
    #     kol_names = filtered_kols_df_coff['KOL Name'].unique()  # Get unique KOL names
    #     selected_kols = st.multiselect("Select KOL Names", options=kol_names)

    #     # Input box for cost
    #     Budget = st.number_input("💰 Enter Budget", min_value=0.0, value=0.1, step=0.01)

    # if selected_kols:  # Check if any KOLs are selected
    #     st.subheader("📊 Results")

    #     # Filter the data based on selected KOL names and platform
    #     selected_kol_data = filtered_kols_df_coff[filtered_kols_df_coff['KOL Name'].isin(selected_kols)]

    #     if not selected_kol_data.empty:
    #         # Ensure 'Value' is numeric and calculate the Budget / Value for each selected KOL using `.loc` to avoid SettingWithCopyWarning
    #         selected_kol_data['Value'] = pd.to_numeric(selected_kol_data['Value'], errors='coerce')  # Convert to numeric
    #         selected_kol_data['Budget / Value'] = Budget / selected_kol_data['Value']  # Calculate Budget / Value

    #         # Display results for each selected KOL
    #         for index, row in selected_kol_data.iterrows():
    #             st.write(f"KOL Name: {row['KOL Name']}")
    #             st.write(f"Platform: {row['Platform']}")
    #             st.write(f"CPX Type: {row['CPX']}")
    #             st.write(f"Budget: {Budget}")

    #             # Determine which calculation to display based on CPX type
    #             if row['CPX'] == 'CPR':
    #                 st.write(f"Calculated Value (Reach): {row['Budget / Value']:.2f}")  # Format to 2 decimal places
    #             elif row['CPX'] == 'CPI':
    #                 st.write(f"Calculated Value (Impression): {row['Budget / Value']:.2f}")
    #             elif row['CPX'] == 'CPE':
    #                 st.write(f"Calculated Value (Engagement): {row['Budget / Value']:.2f}")
    #             elif row['CPX'] == 'CPC':
    #                 st.write(f"Calculated Value (Click): {row['Budget / Value']:.2f}")
    #             elif row['CPX'] == 'CPV':
    #                 st.write(f"Calculated Value (View): {row['Budget / Value']:.2f}")
    #             else:
    #                 st.write(f"Calculated Value: {row['Budget / Value']:.2f}")  # Default case

    #             st.write("---")
    #     else:
    #         st.write("No data found for the selected KOL(s). Please check your selection.")
    # else:
    #     st.write("No KOLs selected. Please select at least one KOL.")


# ---------- PAGE 3: SUMMARY BUDGET ----------
# elif st.session_state.page == "Optimized Budget":
#     st.title("📋 Optimized Budget")

#     def get_weights(category):
#         """Extracts weights by KPI and Tier for the selected category from dataframe"""
#         cat_df = weights_df[weights_df['Category'] == category]
#         impression_weights = cat_df[cat_df['KPI'] == 'Impression'].set_index('Tier')['Weights'].to_dict()
#         view_weights = cat_df[cat_df['KPI'] == 'View'].set_index('Tier')['Weights'].to_dict()
#         engagement_weights = cat_df[cat_df['KPI'] == 'Engagement'].set_index('Tier')['Weights'].to_dict()
#         return impression_weights, view_weights, engagement_weights

#     def optimize_budget(total_budget, min_alloc, max_alloc, priority='balanced', category="F&B"):
#         tiers = ['VIP', 'Mega', 'Macro','Mid', 'Micro', 'Nano']
#         num_tiers = len(tiers)

#         # Get KPI weights based on selected category
#         impression_weights, view_weights, engagement_weights = get_weights(category)

#         # Define KPI objective coefficients based on priority
#         if priority == 'impressions':
#             weights = [impression_weights[t] for t in tiers]
#         elif priority == 'views':
#             weights = [view_weights[t] for t in tiers]
#         elif priority == 'engagement':
#             weights = [engagement_weights[t] for t in tiers]
#         else:  # balanced
#             weights = [(impression_weights[t] + view_weights[t] + engagement_weights[t]) / 3 for t in tiers]

#         # Convert to negative for maximization
#         c = -np.array(weights)

#         # Constraints: Budget and min/max allocations
#         A_eq = [np.ones(num_tiers)]
#         b_eq = [total_budget]

#         bounds = [(min_alloc[t], max_alloc[t]) for t in tiers]

#         # Solve optimization
#         res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

#         if res.success:
#             allocation = {tiers[i]: res.x[i] for i in range(num_tiers)}
#             impressions = sum(res.x[i] * impression_weights[tiers[i]] for i in range(num_tiers))
#             views = sum(res.x[i] * view_weights[tiers[i]] for i in range(num_tiers))
#             engagement = sum(res.x[i] * engagement_weights[tiers[i]] for i in range(num_tiers))
#             total_kpi = impressions + views + engagement
#             return allocation, impressions, views, engagement, total_kpi
#         else:
#             return None, None, None, None, None

#     # Streamlit UI
#     st.title("📊 Budget Optimization Tool")

#     # Category selection
#     categories = weights_df['Category'].unique()
#     category = st.selectbox("Select Category:", categories)

#     # Total Budget input
#     total_budget = st.number_input("Enter Total Budget:", min_value=0, value=10000, step=100)

#     # Min/Max Allocation inputs
#     min_alloc = {}
#     max_alloc = {}
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Minimum Allocation")
#         for tier in ['VIP', 'Mega','Macro', 'Mid', 'Micro', 'Nano']:
#             min_alloc[tier] = st.number_input(f"Min {tier}", min_value=0, value=0)

#     with col2:
#         st.subheader("Maximum Allocation")
#         for tier in ['VIP', 'Mega','Macro', 'Mid', 'Micro', 'Nano']:
#             max_alloc[tier] = st.number_input(f"Max {tier}", min_value=0, value=total_budget)

#     # Priority selection for optimization
#     priority = st.selectbox("Select Optimization Priority:", ["balanced", "impressions", "views", "engagement"])

#     # Optimization button
#     if st.button("Optimize Budget"):
#         allocation, impressions, views, engagement, total_kpi = optimize_budget(total_budget, min_alloc, max_alloc, priority, category)

#         if allocation:
#             st.success("✅ Optimization Successful!")
#             st.json(allocation)

#             st.subheader("📊 KPI Breakdown")
#             st.write(f"Impressions: {impressions:,.2f}")
#             st.write(f"Views: {views:,.2f}")
#             st.write(f"Engagement: {engagement:,.2f}")
#             st.write(f"💰 **Total KPI (Impressions + Views + Engagement)**: {total_kpi:,.2f}")
#         else:
#             st.error("❌ Optimization failed. Check constraints.")

elif st.session_state.page == "Optimized Budget":
    # --------- Config ---------
    TIERS = ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']
    DISPLAY_ORDER = ['Nano', 'Micro', 'Mid', 'Macro', 'Mega', 'VIP']  # stack order (bottom->top)
    
    # --------- Helper functions (self-contained) ---------
    def _validate_and_prepare_weights(weights_df):
        required_cols = {'Category', 'Tier', 'KPI', 'Weights'}
        if 'weights_df' not in globals():
            raise ValueError("weights_df not found in global scope.")
        missing = required_cols - set(weights_df.columns)
        if missing:
            raise ValueError(f"weights_df missing columns: {missing}")
    
        df = weights_df.copy()
        for col in ['Category', 'Tier', 'KPI']:
            df[col] = df[col].astype(str).str.strip()
        df['Weights'] = pd.to_numeric(df['Weights'], errors='coerce')
        if df['Weights'].isna().any():
            raise ValueError("Found non-numeric or missing Weights in weights_df.")
    
        # Normalize KPI labels
        kpi_map = {
            'impression': 'Impression',
            'impressions': 'Impression',
            'view': 'View',
            'views': 'View',
            'engagement': 'Engagement',
        }
        df['KPI'] = df['KPI'].str.lower().map(kpi_map).fillna(df['KPI'])
        return df
    
    def _get_weights_by_kpi(df, category):
        cat_df = df[df['Category'] == category]
        if cat_df.empty:
            raise ValueError(f"No rows found for Category='{category}' in weights_df.")
    
        def to_map(kpi_name):
            sub = cat_df[cat_df['KPI'] == kpi_name]
            if sub.empty:
                raise ValueError(f"No rows found for KPI='{kpi_name}' under Category='{category}'.")
            mp = sub.set_index('Tier')['Weights'].to_dict()
            missing_tiers = [t for t in TIERS if t not in mp]
            if missing_tiers:
                raise ValueError(f"Missing tiers for KPI='{kpi_name}' under Category='{category}': {missing_tiers}")
            return mp
    
        impression_w = to_map('Impression')
        view_w = to_map('View')
        engagement_w = to_map('Engagement')
        return impression_w, view_w, engagement_w
    
    def _build_priority_weights(priority, impression_w, view_w, engagement_w):
        if priority == 'impressions':
            w = [impression_w[t] for t in TIERS]
        elif priority == 'views':
            w = [view_w[t] for t in TIERS]
        elif priority == 'engagement':
            w = [engagement_w[t] for t in TIERS]
        else:  # balanced
            w = [(impression_w[t] + view_w[t] + engagement_w[t]) / 3.0 for t in TIERS]
        return np.array(w, dtype=float)
    
    def _compute_kpis(x, impression_w, view_w, engagement_w):
        imps = float(sum(x[i] * impression_w[TIERS[i]] for i in range(len(TIERS))))
        views = float(sum(x[i] * view_w[TIERS[i]] for i in range(len(TIERS))))
        eng = float(sum(x[i] * engagement_w[TIERS[i]] for i in range(len(TIERS))))
        total_kpi = imps + views + eng
        return imps, views, eng, total_kpi
    
    def _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=None, b_ub=None):
        n = len(TIERS)
        A_eq = [np.ones(n)]
        b_eq = [total_budget]
        bounds = [(min_alloc[t], max_alloc[t]) for t in TIERS]
        return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    def _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category):
        imp_w, view_w, eng_w = _get_weights_by_kpi(df, category)
        weights_vec = _build_priority_weights(priority, imp_w, view_w, eng_w)
        # Maximize weights_vec @ x -> minimize -weights_vec @ x
        res = _solve_lp(-weights_vec, total_budget, min_alloc, max_alloc)
        if not res.success:
            return None
    
        imps, views, eng, total_kpi = _compute_kpis(res.x, imp_w, view_w, eng_w)
        primary_score = float(np.dot(res.x, weights_vec))
    
        return dict(
            x=res.x,
            weights_vec=weights_vec,
            impression_w=imp_w,
            view_w=view_w,
            engagement_w=eng_w,
            primary_score=primary_score,
            imps=imps, views=views, eng=eng, total_kpi=total_kpi
        )
    
    def get_five_budget_scenarios(weights_df, total_budget, min_alloc, max_alloc, priority='balanced', category='Total IPG'):
        # Validate bounds
        invalid_keys = [t for t in TIERS if t not in min_alloc or t not in max_alloc]
        if invalid_keys:
            raise ValueError(f"min_alloc/max_alloc missing keys for tiers: {invalid_keys}")
        if any(min_alloc[t] > max_alloc[t] for t in TIERS):
            bad = [t for t in TIERS if min_alloc[t] > max_alloc[t]]
            raise ValueError(f"Min > Max for tiers: {bad}")
        if sum(min_alloc[t] for t in TIERS) > total_budget:
            raise ValueError("Infeasible: sum of minimum allocations exceeds total budget.")
    
        df = _validate_and_prepare_weights(weights_df)
    
        base = _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category)
        if base is None:
            return []
    
        x_star = base['x']
        weights_vec = base['weights_vec']
        imp_w, view_w, eng_w = base['impression_w'], base['view_w'], base['engagement_w']
        z_star = base['primary_score']
    
        scenarios = []
    
        def pack(label, x_vec):
            alloc = {TIERS[i]: float(x_vec[i]) for i in range(len(TIERS))}
            imps, views, eng, total_kpi = _compute_kpis(x_vec, imp_w, view_w, eng_w)
            return dict(
                label=label,
                allocation=alloc,
                impressions=float(imps),
                views=float(views),
                engagement=float(eng),
                total_kpi=float(total_kpi),
                primary_score=float(np.dot(x_vec, weights_vec))
            )
    
        # 1) Optimal
        scenarios.append(pack("Optimal", x_star))
    
        # 2) Near-optimal alternatives: emphasize each tier within fixed KPI tolerance
        epsilon_pct = 1.5
        eps_abs = abs(z_star) * (epsilon_pct / 100.0)
        # Constraint: weights_vec @ x >= z_star - eps_abs -> -weights_vec @ x <= -(z_star - eps_abs)
        A_ub = [-weights_vec]
        b_ub = [-(z_star - eps_abs)]
    
        for i, t in enumerate(TIERS):
            c = np.zeros(len(TIERS))
            c[i] = -1.0  # maximize allocation for tier t
            res = _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=A_ub, b_ub=b_ub)
            if res.success:
                scenarios.append(pack(f"Near-optimal (emphasize {t})", res.x))
    
        # Deduplicate by rounded allocation pattern
        def key(s):
            return tuple(round(s['allocation'][t], 2) for t in TIERS)
    
        uniq = {}
        for s in scenarios:
            uniq.setdefault(key(s), s)
        uniq_list = list(uniq.values())
    
        # Sort and take up to 5
        uniq_list.sort(key=lambda s: s['primary_score'], reverse=True)
        top5 = uniq_list[:5]
    
        # If fewer than 5, tilt the objective to diversify
        i_try = 0
        seen_keys = {key(s) for s in top5}
        while len(top5) < 5 and i_try < 10:
            bias = np.zeros(len(TIERS))
            bias[i_try % len(TIERS)] = max(1.0, np.max(weights_vec) * 0.15)
            res = _solve_lp(-(weights_vec + bias), total_budget, min_alloc, max_alloc)
            if res.success:
                cand = pack(f"Alternative (tilt {TIERS[i_try % len(TIERS)]})", res.x)
                k = key(cand)
                if k not in seen_keys:
                    top5.append(cand)
                    seen_keys.add(k)
            i_try += 1
    
        return top5[:5]
    
    # --------- UI ---------
    st.title("📊 Budget Optimization Tool (5 Scenarios)")
    
    # Check weights_df presence
    if 'weights_df' not in globals():
        st.error("weights_df not found. Load your Google Sheet into a DataFrame named 'weights_df' before this page runs.")
        st.stop()
    
    # Categories from weights_df
    try:
        df_clean = _validate_and_prepare_weights(weights_df)
    except Exception as e:
        st.error(str(e))
        st.stop()
    
    categories = sorted(df_clean['Category'].dropna().unique().tolist())
    if not categories:
        st.error("No categories found in weights_df.")
        st.stop()
    
    default_idx = 0
    if "Total IPG" in categories:
        default_idx = categories.index("Total IPG")
    category = st.selectbox("Select Category:", options=categories, index=default_idx)
    
    # Budget input
    total_budget = st.number_input("Enter Total Budget:", min_value=0.0, value=10000.0, step=100.0)
    
    # Min/Max allocations
    min_alloc, max_alloc = {}, {}
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Minimum Allocation")
        for t in TIERS:
            min_alloc[t] = st.number_input(f"Min {t}", min_value=0.0, value=0.0, step=100.0, key=f"min_{t}")
    with col2:
        st.subheader("Maximum Allocation")
        for t in TIERS:
            max_alloc[t] = st.number_input(f"Max {t}", min_value=0.0, value=total_budget, step=100.0, key=f"max_{t}")
    
    # Priority
    priority = st.selectbox("Select Optimization Priority:", ["balanced", "impressions", "views", "engagement"])
    
    # Run
    if st.button("Generate 5 scenarios"):
        # Feasibility checks
        if any(min_alloc[t] > max_alloc[t] for t in TIERS):
            bad = [t for t in TIERS if min_alloc[t] > max_alloc[t]]
            st.error(f"Infeasible: Min > Max for {', '.join(bad)}")
            st.stop()
        if sum(min_alloc[t] for t in TIERS) > total_budget:
            st.error("Infeasible: Sum of minimum allocations exceeds total budget.")
            st.stop()
    
        try:
            scenarios = get_five_budget_scenarios(
                weights_df=weights_df,
                total_budget=float(total_budget),
                min_alloc={k: float(v) for k, v in min_alloc.items()},
                max_alloc={k: float(v) for k, v in max_alloc.items()},
                priority=priority,
                category=category
            )
        except Exception as e:
            st.exception(e)
            st.stop()
    
        if not scenarios:
            st.error("No feasible scenarios found with the given constraints.")
        else:
            st.success("✅ Generated up to 5 scenarios")
    
            # Build one DataFrame for a single stacked bar chart
            scenario_labels = [f"S{i+1}: {s['label']}" for i, s in enumerate(scenarios)]
            records = []
            for idx, s in enumerate(scenarios):
                scen_name = scenario_labels[idx]
                for tier in DISPLAY_ORDER:
                    records.append({
                        "Scenario": scen_name,
                        "Tier": tier,
                        "Allocation": s['allocation'].get(tier, 0.0)
                    })
            chart_df = pd.DataFrame(records)
    
            # Stacked bar chart (one chart, stacks by tier within each scenario)
            chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    x=alt.X("Scenario:N", sort=scenario_labels, title="Scenario"),
                    y=alt.Y("Allocation:Q", stack="zero", title="Allocation"),
                    color=alt.Color(
                        "Tier:N",
                        sort=DISPLAY_ORDER,
                        scale=alt.Scale(domain=DISPLAY_ORDER),
                        title="Tier"
                    ),
                    order=alt.Order("Tier:N", sort=DISPLAY_ORDER),
                    tooltip=[
                        alt.Tooltip("Scenario:N"),
                        alt.Tooltip("Tier:N"),
                        alt.Tooltip("Allocation:Q", format=",.2f"),
                    ],
                )
                .properties(height=420)
            )
            st.altair_chart(chart, use_container_width=True)
    
            # KPI table
            kpi_rows = []
            for idx, s in enumerate(scenarios):
                kpi_rows.append({
                    "Scenario": scenario_labels[idx],
                    "Impressions": s['impressions'],
                    "Views": s['views'],
                    "Engagement": s['engagement'],
                    "Total KPI": s['total_kpi'],
                })
            kpi_df = pd.DataFrame(kpi_rows)
            st.dataframe(
                kpi_df.style.format({
                    "Impressions": "{:,.2f}",
                    "Views": "{:,.2f}",
                    "Engagement": "{:,.2f}",
                    "Total KPI": "{:,.2f}",
                }),
                hide_index=True,
                use_container_width=True
            )
    
#Page4
if st.session_state.page == "GEN AI":
    st.title(" COMMING SOON...")
    # import pydata_google_auth
    
    # SCOPES = [
    #     'https://www.googleapis.com/auth/cloud-platform',
    #     'https://www.googleapis.com/auth/drive',
    # ]
    
    # credentials = pydata_google_auth.get_user_credentials(
    #     SCOPES,
    #     auth_local_webserver=True,
    # )
    
    # query = """
    # SELECT * FROM `pj-allclient-4d2mru.view.industry_norm_fbgg_category_stats_view`
    # """
    # df = pd.read_gbq(query=query, project_id = "pj-newnestle-vmtifr", credentials=credentials, dialect = 'standard')
    
    # # Show the data in Streamlit
    # st.dataframe(df)
# # Page 4: GEN AI with PandasAI (Free Hugging Face Model, No API Key + Clear Chat)

# if st.session_state.page == "GEN AI":
#     import streamlit as st
#     import pandas as pd
#     from pandasai import SmartDataframe
#     from transformers import pipeline
#     from pandasai.llm.base import LLM

#     # Local model wrapper
#     class LocalHuggingFaceLLM(LLM):
#         def __init__(self, model_name="google/flan-t5-base"):
#             self.model_name = model_name
#             self.generator = pipeline("text2text-generation", model=model_name)

#         def call(self, prompt: str, *args, **kwargs) -> str:
#             result = self.generator(prompt, max_length=256, do_sample=True)[0]["generated_text"]
#             return result

#         @property
#         def type(self):
#             return "local-huggingface"

#     st.title("📊 GEN AI: Chat with Your Data (No API Key)")

#     # Session state for chat
#     if "chat_prompt" not in st.session_state:
#         st.session_state.chat_prompt = ""
#     if "chat_response" not in st.session_state:
#         st.session_state.chat_response = ""

#     uploaded_file = st.file_uploader("📎 Upload a CSV file", type=["csv"])
#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
#         st.write("🧾 Data Preview:", df.head())

#         llm = LocalHuggingFaceLLM()

#         sdf = SmartDataframe(
#             df,
#             config={
#                 "llm": llm,
#                 "enable_cache": False,
#                 "enable_memory": True,
#                 "verbose": True,
#             },
#         )

#         # Input + buttons
#         col1, col2 = st.columns([3, 1])
#         with col1:
#             st.session_state.chat_prompt = st.text_input(
#                 "💬 Ask a question about your data (e.g. 'Which category has the lowest CPM?')",
#                 value=st.session_state.chat_prompt,
#                 key="prompt_input"
#             )

#         with col2:
#             if st.button("🧹 Clear Chat"):
#                 st.session_state.chat_prompt = ""
#                 st.session_state.chat_response = ""

#         # Handle question
#         if st.session_state.chat_prompt:
#             with st.spinner("🤖 Thinking..."):
#                 try:
#                     st.session_state.chat_response = sdf.chat(st.session_state.chat_prompt)
#                 except Exception as e:
#                     st.session_state.chat_response = f"❌ Error: {e}"

#         # Show response
#         if st.session_state.chat_response:
#             st.write("✅ Response:", st.session_state.chat_response)

# ---------- Page 5: Embedded Looker Studio Dashboard ----------
if st.session_state.page == "Dashboard":
    st.title("📊 Live Dashboard")
    st.markdown("Click below to view your dashboard in a new tab:")

    # # Display an image or icon (optional)
    # st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Google_Data_Studio_Logo.svg/512px-Google_Data_Studio_Logo.svg.png", width=100)

    # Add a button to open the Looker Studio link
    dashboard_url = "https://lookerstudio.google.com/reporting/2612a10a-44a2-4b2d-866d-58b4cd13023e/page/bIqhE"
    st.markdown(f"""
        <a href="{dashboard_url}" target="_blank">
            <button style="background-color:#4285F4;color:white;padding:10px 20px;border:none;border-radius:8px;font-size:16px;">
                🔗 Open Dashboard
            </button>
        </a>
    """, unsafe_allow_html=True)
