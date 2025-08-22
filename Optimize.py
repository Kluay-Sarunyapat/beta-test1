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
st.set_page_config(page_title="MBCS Optimize Tool", page_icon="📁", layout="wide")

# Init session state
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "prev_page" not in st.session_state:
    st.session_state.prev_page = None

def change_page(name: str):
    st.session_state.prev_page = st.session_state.page
    st.session_state.page = name

# Global styles + Effects
st.markdown(
    """
    <style>
    :root{
      --p1:#6a5acd; --p2:#00e5ff; --p3:#ff7bd5; --p4:#8affc1;
      --bg1:#0e1022; --bg2:#171a35; --glass:rgba(255,255,255,.08);
    }
    /* App background */
    [data-testid="stAppViewContainer"]{
      background: radial-gradient(1200px 500px at 10% 0%, rgba(0,229,255,.06), transparent),
                  radial-gradient(1200px 500px at 90% 0%, rgba(255,123,213,.06), transparent),
                  linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
      color: #e9ecff;
      padding-top: 1.2rem;
    }

    /* Header card */
    .app-header{
      position: relative; overflow: hidden; padding: 28px 28px 22px;
      border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 18px 60px rgba(0,0,0,.35), inset 0 0 40px rgba(255,255,255,.02);
      margin-bottom: 18px;
    }
    .app-header:before{
      content:""; position:absolute; inset:-2px;
      background: conic-gradient(from 0deg, var(--p1), var(--p2), var(--p3), var(--p1));
      filter: blur(28px); opacity:.35; animation: spin 8s linear infinite;
    }
    .headline{
      font-size: clamp(26px, 4.2vw, 44px); font-weight: 900; letter-spacing:.4px;
      background: linear-gradient(90deg, #fff, #cfe9ff, #ffffff);
      -webkit-background-clip: text; background-clip: text; color: transparent;
      text-shadow: 0 0 18px rgba(0,229,255,.25);
    }
    .subline{
      margin-top: 6px; color:#c9d4ff; opacity:.9; font-size: clamp(12px, 1.6vw, 14px);
    }
    .shine{
      position:absolute; inset:1px; border-radius:16px;
      background: linear-gradient(120deg, rgba(255,255,255,.22), transparent 30%, transparent 70%, rgba(255,255,255,.22));
      background-size: 220% 100%; animation: shine 3.6s linear infinite;
      pointer-events:none;
    }

    /* Buttons */
    div.stButton > button{
      width: 100%;
      border-radius: 14px;
      padding: 0.85rem 1rem;
      border: 1px solid rgba(255,255,255,.18);
      color: #fff; font-weight: 800; letter-spacing:.2px;
      background: linear-gradient(135deg, rgba(106,90,205,.85), rgba(0,229,255,.55));
      box-shadow: 0 12px 28px rgba(68,144,255,.28), inset 0 0 18px rgba(255,255,255,.06);
      transition: transform .15s ease, box-shadow .2s ease, filter .2s ease;
      backdrop-filter: blur(6px);
    }
    div.stButton > button:hover{
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 18px 36px rgba(68,144,255,.38);
      filter: brightness(1.05);
      cursor: pointer;
    }
    div.stButton > button:active{
      transform: translateY(0) scale(.98);
    }

    /* Current page pill */
    .page-pill{
      display: inline-flex; align-items: center; gap:10px;
      padding: 10px 16px; margin-top: 8px;
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(106,90,205,.4), rgba(0,229,255,.25));
      border: 1px solid rgba(255,255,255,.18);
      color: #f4f7ff; font-weight: 700;
      box-shadow: 0 0 0 0 rgba(106,90,205,.45);
      animation: pulse 2.4s infinite;
      position: relative; overflow: hidden;
    }
    .page-pill .dot{
      width: 10px; height: 10px; border-radius: 50%;
      background: var(--p4); box-shadow: 0 0 12px var(--p4);
    }
    .page-pill .glowline{
      position:absolute; inset:1px; border-radius:999px;
      background: linear-gradient(120deg, rgba(255,255,255,.22), transparent 40%, transparent 60%, rgba(255,255,255,.22));
      background-size: 200% 100%; animation: shine 3.2s linear infinite;
      pointer-events:none;
    }

    @keyframes shine{
      0%{ background-position: 200% 0; } 100%{ background-position: -200% 0; }
    }
    @keyframes pulse{
      0%{ box-shadow: 0 0 0 0 rgba(106,90,205,.45); }
      70%{ box-shadow: 0 0 0 14px rgba(106,90,205,0); }
      100%{ box-shadow: 0 0 0 0 rgba(106,90,205,0); }
    }
    @keyframes spin{ to{ transform: rotate(360deg);} }
    </style>
    """,
    unsafe_allow_html=True
)

# Fancy header
st.markdown(
    """
    <div class="app-header">
      <div class="shine"></div>
      <div class="headline">📁 Welcome To MBCS Optimize Tool</div>
      <div class="subline">Smart budget simulation • Influencer performance • Optimization</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("📂 Simulation Budget"):
        change_page("Simulation Budget")

with col2:
    if st.button("💰 Influencer Performance"):
        change_page("Influencer Performance")

with col3:
    if st.button("📋 Optimized Budget"):
        change_page("Optimized Budget")

# Animated Current Page pill
curr = st.session_state.page
st.markdown(
    f"""
    <div class="page-pill">
      <span class="dot"></span>
      <span>Current Page: <strong>{curr}</strong></span>
      <div class="glowline"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Optional: subtle toast when page changes
if st.session_state.prev_page and st.session_state.prev_page != st.session_state.page:
    st.toast(f"Switched to: {st.session_state.page}", icon="✨")

# Example content area (optional)
st.write("")
if curr == "Simulation Budget":
    st.subheader("Simulation Budget")
    st.write("ใส่พารามิเตอร์งบประมาณและรันจำลองที่นี่")
elif curr == "Influencer Performance":
    st.subheader("Influencer Performance")
    st.write("อัปโหลด/ดูผลลัพธ์ของอินฟลูเอนเซอร์ที่นี่")
elif curr == "Optimized Budget":
    st.subheader("Optimized Budget")
    st.write("ดูงบประมาณที่ถูก Optimize แล้วที่นี่")
else:
    st.subheader("Home")
    st.write("เลือกเมนูด้านบนเพื่อเริ่มต้น")

# st.markdown("### 📁 Welcome To MBCS Optimize Tool")
# col1, col2, col3, = st.columns([1, 1, 1])  # Equal column widths
# #col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Equal column widths

# with col1:
#     if st.button("📂 Simulation Budget"):
#         change_page("Simulation Budget")

# with col2:
#     if st.button("💰 Influencer Performance"):
#         change_page("Influencer Performance")

# with col3:
#     if st.button("📋 Optimized Budget"):
#         change_page("Optimized Budget")

# # with col4:
# #     if st.button("🤖 GEN AI"):
# #         change_page("GEN AI")

# # with col5:
# #     if st.button("📊 Dashboard"):
# #         change_page("Dashboard")

# st.write(f"Current Page: {st.session_state.page}")


# ---------- FUNCTION: Load Weights from Google Sheet CSV ----------
@st.cache_data
def load_weights(csv_url):
    df = pd.read_csv(csv_url)
    return df

# Load weights from the published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/1CG19lrXCDYLeyPihaq4xwuPSw86oQUNB/export?format=csv"
weights_df = load_weights(csv_url)

# ---------- PAGE 1: Initialize session state ----------

if st.session_state.page == "Simulation Budget":

    # ---------- Title ----------
    st.title("📊 Simulation Budget")
    
    # ---------- Config ----------
    TIERS = ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']
    
    # ---------- Validate weights_df ----------
    required_cols = {'Category', 'Tier', 'Platform', 'KPI', 'Weights'}
    missing_cols = required_cols - set(weights_df.columns)
    if missing_cols:
        st.error(f"weights_df missing columns: {missing_cols}")
        st.stop()
    
    weights_df = weights_df.copy()
    for c in ['Category', 'Tier', 'Platform', 'KPI']:
        weights_df[c] = weights_df[c].astype(str).str.strip()
    weights_df['Weights'] = pd.to_numeric(weights_df['Weights'], errors='coerce')
    
    # ---------- Initialize Session State ----------
    if 'inputs_a' not in st.session_state:
        st.session_state.inputs_a = dict(VIP=0, Mega=0, Macro=0, Mid=0, Micro=0, Nano=0)
    if 'inputs_b' not in st.session_state:
        st.session_state.inputs_b = dict(VIP=0, Mega=0, Macro=0, Mid=0, Micro=0, Nano=0)
    if 'inputs_c' not in st.session_state:
        st.session_state.inputs_c = dict(VIP=0, Mega=0, Macro=0, Mid=0, Micro=0, Nano=0)
    
    available_categories = sorted(weights_df['Category'].dropna().unique().tolist())
    if len(available_categories) == 0:
        st.error("No categories found in weights_df.")
        st.stop()
    
    if 'category_a' not in st.session_state:
        st.session_state.category_a = available_categories[0]
    if 'category_b' not in st.session_state:
        st.session_state.category_b = available_categories[0]
    if 'category_c' not in st.session_state:
        st.session_state.category_c = available_categories[0]
    
    # ---------- Helpers ----------
    def platforms_for_category(cat):
        return sorted(
            weights_df.loc[weights_df['Category'] == cat, 'Platform']
            .dropna().unique().tolist()
        )
    
    if 'platform_a' not in st.session_state:
        pa = platforms_for_category(st.session_state.category_a)
        st.session_state.platform_a = pa[0] if pa else None
    if 'platform_b' not in st.session_state:
        pb = platforms_for_category(st.session_state.category_b)
        st.session_state.platform_b = pb[0] if pb else None
    if 'platform_c' not in st.session_state:
        pc = platforms_for_category(st.session_state.category_c)
        st.session_state.platform_c = pc[0] if pc else None
    
    def get_weights(category, platform, kpi):
        if platform is None:
            return {}
        filt = (
            (weights_df['Category'] == category) &
            (weights_df['Platform'] == platform) &
            (weights_df['KPI'] == kpi)
        )
        sub = weights_df.loc[filt, ['Tier', 'Weights']].copy()
        if sub.empty:
            return {}
        sub['Weights'] = pd.to_numeric(sub['Weights'], errors='coerce')
        return {row['Tier']: (0.0 if pd.isna(row['Weights']) else float(row['Weights'])) for _, row in sub.iterrows()}
    
    def colored_percentage(p):
        if p >= 40:
            return f"<span style='color:#1E90FF;font-weight:bold;'>{p:.1f}%</span>"
        elif p >= 20:
            return f"<span style='color:#FF9800;font-weight:bold;'>{p:.1f}%</span>"
        elif p > 0:
            return f"<span style='color:#009688;'>{p:.1f}%</span>"
        else:
            return "<span style='color:#aaa;'>0.0%</span>"
    
    # ---------- Panels ----------
    st.subheader("📊 Budget Simulation Comparison")
    col_input_a, col_input_b, col_input_c = st.columns(3)
    
    def inputs_panel(col, sim_key, cat_key, plat_key, inputs_key, bg_color, title_color):
        with col:
            st.subheader(f"Simulation {sim_key.upper()}")
    
            st.session_state[cat_key] = st.selectbox(
                f"Simulation {sim_key.upper()} - Category:",
                available_categories,
                key=f"cat_{sim_key}",
                index=available_categories.index(st.session_state[cat_key])
            )
    
            plats = platforms_for_category(st.session_state[cat_key])
            display_options = plats if plats else ['(None)']
            current = st.session_state.get(plat_key, display_options[0])
            if current not in display_options:
                current = display_options[0]
            sel = st.selectbox(
                f"Simulation {sim_key.upper()} - Platform:",
                display_options,
                key=f"plat_{sim_key}",
                index=display_options.index(current)
            )
            st.session_state[plat_key] = None if sel == '(None)' else sel
    
            new_inputs = {}
            for t in st.session_state[inputs_key]:
                cols = st.columns([3, 2])
                val = cols[0].number_input(f"{t}", min_value=0, value=st.session_state[inputs_key][t], key=f"{sim_key}_{t}")
                new_inputs[t] = val
                total_new = sum(new_inputs.values())
                percent = (val / total_new) * 100 if total_new > 0 else 0
                cols[1].markdown(colored_percentage(percent), unsafe_allow_html=True)
            st.session_state[inputs_key] = new_inputs
    
            total_final = sum(new_inputs.values())
            st.markdown(
                f"""
                <div style="background-color:{bg_color};padding:15px 0 15px 0;border-radius:12px;text-align:center;box-shadow:0 2px 5px #00000022;">
                    <div style="font-size:2.3rem;font-weight:bold;color:{title_color};">{total_final:,}</div>
                    <div style="font-size:1.2rem;">💰 Total Budget {sim_key.upper()}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    inputs_panel(col_input_a, 'a', 'category_a', 'platform_a', 'inputs_a', '#e0f7fa', '#0277bd')
    inputs_panel(col_input_b, 'b', 'category_b', 'platform_b', 'inputs_b', '#f3e5f5', '#8e24aa')
    inputs_panel(col_input_c, 'c', 'category_c', 'platform_c', 'inputs_c', '#e8f5e9', '#2e7d32')
    
    # ---------- Metric calculations ----------
    def calc_metrics(inputs, category, platform):
        impression_weights  = get_weights(category, platform, "Impression")
        view_weights        = get_weights(category, platform, "View")
        engagement_weights  = get_weights(category, platform, "Engagement")
        share_weights       = get_weights(category, platform, "Share")
    
        total_impressions = sum(inputs.get(k, 0) * impression_weights.get(k, 0) for k in inputs)
        total_views       = sum(inputs.get(k, 0) * view_weights.get(k, 0)       for k in inputs)
        total_engagement  = sum(inputs.get(k, 0) * engagement_weights.get(k, 0) for k in inputs)
        total_share       = sum(inputs.get(k, 0) * share_weights.get(k, 0)       for k in inputs)
    
        return total_impressions, total_views, total_engagement, total_share
    
    imp_a, view_a, eng_a, share_a = calc_metrics(st.session_state.inputs_a, st.session_state.category_a, st.session_state.platform_a)
    imp_b, view_b, eng_b, share_b = calc_metrics(st.session_state.inputs_b, st.session_state.category_b, st.session_state.platform_b)
    imp_c, view_c, eng_c, share_c = calc_metrics(st.session_state.inputs_c, st.session_state.category_c, st.session_state.platform_c)
    
    budget_a = sum(st.session_state.inputs_a.values())
    budget_b = sum(st.session_state.inputs_b.values())
    budget_c = sum(st.session_state.inputs_c.values())
    
    # ---------- Highlight ----------
    def highlight3(a, b, c):
        vals = [a, b, c]
        maxv = max(vals)
        top_count = vals.count(maxv)
        styled = []
        for v in vals:
            if v == maxv and top_count >= 2:
                styled.append(f"<span style='color:#1e88e5;font-weight:bold;font-size:1.2em'>{v:,.0f}</span>")
            elif v == maxv:
                styled.append(f"<span style='color:#388e3c;font-weight:bold;font-size:1.25em'>{v:,.0f}</span>")
            else:
                styled.append(f"<span style='color:#aaa;font-size:1.08em'>{v:,.0f}</span>")
        return tuple(styled)
    
    def highlight3_low(a, b, c):
        vals = [a, b, c]
        minv = min(vals)
        low_count = vals.count(minv)
        styled = []
        for v in vals:
            disp = f"{v:,.2f}"
            if v == minv and low_count >= 2:
                styled.append(f"<span style='color:#1e88e5;font-weight:bold;font-size:1.2em'>{disp}</span>")
            elif v == minv:
                styled.append(f"<span style='color:#388e3c;font-weight:bold;font-size:1.25em'>{disp}</span>")
            else:
                styled.append(f"<span style='color:#aaa;font-size:1.08em'>{disp}</span>")
        return tuple(styled)
    
    imp_a_html,   imp_b_html,   imp_c_html   = highlight3(imp_a,  imp_b,  imp_c)
    view_a_html,  view_b_html,  view_c_html  = highlight3(view_a, view_b, view_c)
    eng_a_html,   eng_b_html,   eng_c_html   = highlight3(eng_a,  eng_b,  eng_c)
    share_a_html, share_b_html, share_c_html = highlight3(share_a, share_b, share_c)
    budget_a_html, budget_b_html, budget_c_html = highlight3(budget_a, budget_b, budget_c)
    
    cpe_a = (budget_a / eng_a) if eng_a > 0 else 0
    cpe_b = (budget_b / eng_b) if eng_b > 0 else 0
    cpe_c = (budget_c / eng_c) if eng_c > 0 else 0
    
    cpshare_a = (budget_a / share_a) if share_a > 0 else 0
    cpshare_b = (budget_b / share_b) if share_b > 0 else 0
    cpshare_c = (budget_c / share_c) if share_c > 0 else 0
    
    cpe_a_html,     cpe_b_html,     cpe_c_html     = highlight3_low(cpe_a, cpe_b, cpe_c)
    cpshare_a_html, cpshare_b_html, cpshare_c_html = highlight3_low(cpshare_a, cpshare_b, cpshare_c)
    
    # ---------- Results ----------
    st.markdown("---")
    st.subheader("📈 Simulation Results Comparison")
    
    html_table = f"""
    <table style="width:92%;margin:auto;border-collapse:collapse;font-size:1.17em;">
      <tr style="background-color:#f0f2f6;">
        <th style="width:20%"></th>
        <th style="color:#0277bd;">Simulation A</th>
        <th style="color:#8e24aa;">Simulation B</th>
        <th style="color:#2e7d32;">Simulation C</th>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Category</td>
        <td>{st.session_state.category_a}</td>
        <td>{st.session_state.category_b}</td>
        <td>{st.session_state.category_c}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Platform</td>
        <td>{st.session_state.platform_a if st.session_state.platform_a is not None else '-'}</td>
        <td>{st.session_state.platform_b if st.session_state.platform_b is not None else '-'}</td>
        <td>{st.session_state.platform_c if st.session_state.platform_c is not None else '-'}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Budget</td>
        <td>{budget_a_html}</td>
        <td>{budget_b_html}</td>
        <td>{budget_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Impressions</td>
        <td>{imp_a_html}</td>
        <td>{imp_b_html}</td>
        <td>{imp_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Views</td>
        <td>{view_a_html}</td>
        <td>{view_b_html}</td>
        <td>{view_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Engagements</td>
        <td>{eng_a_html}</td>
        <td>{eng_b_html}</td>
        <td>{eng_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">Shares</td>
        <td>{share_a_html}</td>
        <td>{share_b_html}</td>
        <td>{share_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">CPE</td>
        <td>{cpe_a_html}</td>
        <td>{cpe_b_html}</td>
        <td>{cpe_c_html}</td>
      </tr>
    
      <tr>
        <td style="font-weight:bold">CPShare</td>
        <td>{cpshare_a_html}</td>
        <td>{cpshare_b_html}</td>
        <td>{cpshare_c_html}</td>
      </tr>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)
    
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
    
    # --------------------- Tier Selection ---------------------
    all_tiers = ['All', 'VIP', 'Mega', 'Mid', 'Macro', 'Micro', 'Nano']
    
    if 'tier_selection' not in st.session_state:
        st.session_state.tier_selection = ['All']
    
    def update_tiers():
        selected = st.session_state['tier_multiselect']
        if 'All' in selected:
            st.session_state.tier_selection = ['All']
        else:
            st.session_state.tier_selection = selected
    
    tier_selection = st.multiselect(
        "🏷️ Tier Selection",
        options=all_tiers,
        default=st.session_state.tier_selection,
        key='tier_multiselect',
        on_change=update_tiers
    )
    
    if 'All' in st.session_state.tier_selection:
        filtered_tiers = None
    else:
        filtered_tiers = [t.lower() for t in st.session_state.tier_selection]
    
    # --------------------- Platform Selection ---------------------
    platform_column_exists = 'platform' in df_full.columns
    if platform_column_exists:
        platforms_raw = (
            df_full['platform']
            .astype(str)
            .str.strip()
            .replace({'nan': '', 'None': '', 'NaN': ''})
        )
        unique_platforms = sorted([p for p in platforms_raw.unique().tolist() if p])
        all_platforms = ['All'] + unique_platforms
    else:
        all_platforms = ['All']
    
    if 'platform_selection' not in st.session_state:
        st.session_state.platform_selection = ['All']
    
    def update_platforms():
        selected = st.session_state['platform_multiselect']
        if 'All' in selected:
            st.session_state.platform_selection = ['All']
        else:
            st.session_state.platform_selection = selected
    
    if platform_column_exists:
        platform_selection = st.multiselect(
            "🖥️ Platform Selection",
            options=all_platforms,
            default=st.session_state.platform_selection,
            key='platform_multiselect',
            on_change=update_platforms
        )
    else:
        st.info("No 'platform' column found; platform filtering is disabled.")
        platform_selection = ['All']
    
    if 'All' in st.session_state.platform_selection or not platform_column_exists:
        filtered_platforms = None
    else:
        filtered_platforms = [p.lower() for p in st.session_state.platform_selection]
    
    # --------------------- Category Selection (new) ---------------------
    category_column_exists = 'category' in df_full.columns
    if category_column_exists:
        categories_raw = (
            df_full['category']
            .astype(str)
            .str.strip()
            .replace({'nan': '', 'None': '', 'NaN': ''})
        )
        unique_categories = sorted([c for c in categories_raw.unique().tolist() if c])
        all_categories = ['All'] + unique_categories
    else:
        all_categories = ['All']
    
    if 'category_selection' not in st.session_state:
        st.session_state.category_selection = ['All']
    
    def update_categories():
        selected = st.session_state['category_multiselect']
        if 'All' in selected:
            st.session_state.category_selection = ['All']
        else:
            st.session_state.category_selection = selected
    
    if category_column_exists:
        category_selection = st.multiselect(
            "📂 Category Selection",
            options=all_categories,
            default=st.session_state.category_selection,
            key='category_multiselect',
            on_change=update_categories
        )
    else:
        st.info("No 'category' column found; category filtering is disabled.")
        category_selection = ['All']
    
    if 'All' in st.session_state.category_selection or not category_column_exists:
        filtered_categories = None
    else:
        filtered_categories = [c.lower() for c in st.session_state.category_selection]
    
    # --------------------- KPI Mapping ---------------------
    kpi_map = {
        'total_impression': 'impression',
        'total_engagement': 'engagement',
        'total_view': 'view',
        'total_share': 'share',
    }
    
    # --------------------- Helper Functions ---------------------
    def prepare_df(df_in: pd.DataFrame, kpi_col: str,
                   allowed_tiers=None, allowed_platforms=None, allowed_categories=None) -> pd.DataFrame:
        df_work = df_in.copy()
    
        # Ensure required columns exist
        for col in ['cost', 'impression', 'engagement', 'view', 'share', 'tier', 'platform', 'category']:
            if col not in df_work.columns:
                df_work[col] = pd.NA
    
        # Tier filter
        if allowed_tiers is not None:
            df_work = df_work[df_work['tier'].astype(str).str.lower().isin(allowed_tiers)]
    
        # Platform filter
        if allowed_platforms is not None:
            df_work = df_work[df_work['platform'].astype(str).str.lower().isin(allowed_platforms)]
    
        # Category filter
        if allowed_categories is not None:
            df_work = df_work[df_work['category'].astype(str).str.lower().isin(allowed_categories)]
    
        # Coerce numeric cols
        for col in ['cost', 'impression', 'engagement', 'view', 'share']:
            df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
    
        # Valid rows for cost and KPI
        df_work = df_work[df_work['cost'].notna() & (df_work['cost'] > 0)]
        df_work = df_work[df_work[kpi_col].notna()]
        df_work = df_work.reset_index(drop=True)
    
        return df_work
    
    def summarize_selection(df_sel: pd.DataFrame) -> pd.DataFrame:
        if df_sel is None or df_sel.empty:
            return pd.DataFrame()
        summary = {
            'kol_name': 'TOTAL' if 'kol_name' in df_sel.columns else '',
            'platform': '',
            'cost': df_sel['cost'].sum() if 'cost' in df_sel else 0,
            'impression': df_sel['impression'].sum() if 'impression' in df_sel else 0,
            'engagement': df_sel['engagement'].sum() if 'engagement' in df_sel else 0,
            'view': df_sel['view'].sum() if 'view' in df_sel else 0,
            'share': df_sel['share'].sum() if 'share' in df_sel else 0,
            'followers': '' if 'followers' in df_sel.columns else '',
            'tier': '',
            'score': ''
        }
        return pd.concat([df_sel, pd.DataFrame([summary])], ignore_index=True)
    
    # --------------------- Greedy (single) ---------------------
    def select_kols_greedy(df_in, budget, k, kpi_col,
                           allowed_tiers=None, allowed_platforms=None, allowed_categories=None):
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty:
            return pd.DataFrame()
    
        df_work['score'] = df_work[kpi_col] / df_work['cost']
        df_work = df_work.sort_values('score', ascending=False).reset_index(drop=True)
    
        selected_rows = []
        total_cost = 0.0
    
        for _, row in df_work.iterrows():
            if len(selected_rows) >= k:
                break
            if total_cost + row['cost'] <= budget:
                selected_rows.append(row)
                total_cost += row['cost']
    
        result = pd.DataFrame(selected_rows)
        return summarize_selection(result)
    
    # --------------------- Greedy (multiple portfolios for same K) ---------------------
    def greedy_multiple_scenarios(df_in, budget, k, kpi_col,
                                  allowed_tiers=None, allowed_platforms=None, allowed_categories=None,
                                  num_scenarios=5):
        df_base = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_base.empty:
            return []
    
        scenarios = []
        excluded_idx = set()
    
        for s in range(num_scenarios):
            work = df_base.copy()
            if excluded_idx:
                work = work[~work.index.isin(excluded_idx)].reset_index(drop=True)
                if work.empty:
                    break
    
            # Compute score and sort
            work['score'] = work[kpi_col] / work['cost']
            work = work.sort_values('score', ascending=False)
    
            # Greedy selection on 'work'
            selected_indices = []
            selected_rows = []
            total_cost = 0.0
    
            for i, row in work.iterrows():
                if len(selected_rows) >= k:
                    break
                if total_cost + row['cost'] <= budget:
                    selected_rows.append(row)
                    selected_indices.append(i)
                    total_cost += row['cost']
    
            if not selected_rows:
                break
    
            scenario_df = summarize_selection(pd.DataFrame(selected_rows))
            scenarios.append(scenario_df)
    
            # Diversify: exclude the highest-score item among the chosen in this scenario
            work_chosen = work.loc[selected_indices].copy().sort_values('score', ascending=False)
            if not work_chosen.empty:
                key_cols = [c for c in ['kol_name', 'platform', 'cost'] if c in df_base.columns]
                if key_cols:
                    key_vals = tuple(work_chosen.iloc[0][key_cols].tolist())
                    mask = pd.Series([True] * len(df_base))
                    for c, v in zip(key_cols, key_vals):
                        mask &= (df_base[c] == v)
                    idx_to_exclude = df_base[mask].index.tolist()
                    if idx_to_exclude:
                        excluded_idx.add(idx_to_exclude[0])
                else:
                    excluded_idx.add(work_chosen.index[0])
    
        return scenarios
    
    # --------------------- LP (single) ---------------------
    def optimize_kols_lp_single(df_in, budget, k, kpi_col,
                                allowed_tiers=None, allowed_platforms=None, allowed_categories=None,
                                exact_k=False):
        try:
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        except Exception:
            st.error("PuLP not installed. Please install with: pip install pulp")
            return pd.DataFrame()
    
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty:
            return pd.DataFrame()
    
        # Cap candidates for speed
        if len(df_work) > 200:
            df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
    
        n = len(df_work)
        prob = LpProblem("KOL_Selection", LpMaximize)
        x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(n)]
    
        prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
        prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
        if exact_k:
            prob += lpSum(x[i] for i in range(n)) == k
        else:
            prob += lpSum(x[i] for i in range(n)) <= k
    
        status = prob.solve()
        try:
            if LpStatus[status] != 'Optimal':
                return pd.DataFrame()
        except Exception:
            pass
    
        chosen_idx = [i for i in range(n) if x[i].varValue == 1]
        result = df_work.loc[chosen_idx].copy()
        return summarize_selection(result)
    
    # --------------------- LP (multiple portfolios for same K) ---------------------
    def optimize_kols_lp_multiple(df_in, budget, k, kpi_col,
                                  allowed_tiers=None, allowed_platforms=None, allowed_categories=None,
                                  num_scenarios=5, exact_k=False):
        try:
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        except Exception:
            st.error("PuLP not installed. Please install with: pip install pulp")
            return []
    
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty:
            return []
    
        # Cap candidates for speed
        if len(df_work) > 200:
            df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
    
        n = len(df_work)
        scenarios = []
        cuts = []  # sets of chosen indices
    
        for s in range(num_scenarios):
            prob = LpProblem(f"KOL_Selection_{s+1}", LpMaximize)
            x = [LpVariable(f"x_{i}_{s}", cat=LpBinary) for i in range(n)]
    
            prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
            prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
            if exact_k:
                prob += lpSum(x[i] for i in range(n)) == k
            else:
                prob += lpSum(x[i] for i in range(n)) <= k
    
            # No-good cuts to enforce diversity
            for sel_set in cuts:
                prob += lpSum(x[i] for i in sel_set) <= max(0, len(sel_set) - 1)
    
            status = prob.solve()
            try:
                if LpStatus[status] != 'Optimal':
                    break
            except Exception:
                pass
    
            chosen_idx = [i for i in range(n) if x[i].varValue == 1]
            if not chosen_idx:
                break
    
            cuts.append(set(chosen_idx))
            scenarios.append(summarize_selection(df_work.loc[chosen_idx].copy()))
    
        return scenarios
    
    # --------------------- Optimizer UI ---------------------
    st.header("🎯 KOL Selection Optimizer")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selection_mode = st.radio("🔀 Optimization Method", ["Greedy", "Linear Programming"], horizontal=False)
    with col2:
        budget = st.number_input("💰 Total Budget (THB)", min_value=0, value=250000, step=1000)
    with col3:
        kpi_option = st.selectbox(
            "📊 KPI Focus",
            options=['total_impression', 'total_engagement', 'total_view', 'total_share']
        )
    
    kpi_col = kpi_map[kpi_option]
    
    st.subheader("🧪 Scenario Mode")
    scenario_mode = st.radio("Choose scenario mode", ["By K values", "Multiple portfolios (same K)"], horizontal=True)
    
    # Inputs per scenario mode
    if scenario_mode == "By K values":
        k_values_str = st.text_input("Enter K values (comma-separated)", value="2,3,5")
        try:
            k_values = [int(x.strip()) for x in k_values_str.split(",") if x.strip().isdigit()]
        except Exception:
            k_values = []
        exact_k = False
        if selection_mode == "Linear Programming":
            exact_k = st.checkbox("Force exactly K KOLs (LP only)", value=False,
                                  help="If off, LP may choose fewer KOLs if the budget is too tight.")
    else:
        fixed_k = st.number_input("🔢 Number of KOLs (K)", min_value=1, value=5, step=1)
        num_scenarios = st.number_input("How many scenarios?", min_value=2, value=5, step=1)
        exact_k = False
        if selection_mode == "Linear Programming":
            exact_k = st.checkbox("Force exactly K KOLs (LP only)", value=False)
    
    # --------------------- Run Optimization ---------------------
    if st.button("🚀 Run Optimization"):
        allowed_tiers = filtered_tiers
        allowed_platforms = filtered_platforms
        allowed_categories = filtered_categories
    
        if scenario_mode == "By K values":
            if not k_values:
                st.warning("Please provide at least one valid K.")
            else:
                st.success("✅ Optimization complete!")
                for k in k_values:
                    st.subheader(f"Scenario: best portfolio for K = {k}")
                    if selection_mode == "Greedy":
                        res = select_kols_greedy(
                            df_full, budget, k, kpi_col,
                            allowed_tiers, allowed_platforms, allowed_categories
                        )
                    else:
                        res = optimize_kols_lp_single(
                            df_full, budget, k, kpi_col,
                            allowed_tiers, allowed_platforms, allowed_categories,
                            exact_k=exact_k
                        )
                    if res.empty:
                        st.info("No feasible selection under budget.")
                    else:
                        st.dataframe(res, use_container_width=True)
        else:
            st.success("✅ Optimization complete!")
            if selection_mode == "Greedy":
                scenarios = greedy_multiple_scenarios(
                    df_full, budget, fixed_k, kpi_col,
                    allowed_tiers, allowed_platforms, allowed_categories,
                    num_scenarios=num_scenarios
                )
            else:
                scenarios = optimize_kols_lp_multiple(
                    df_full, budget, fixed_k, kpi_col,
                    allowed_tiers, allowed_platforms, allowed_categories,
                    num_scenarios=num_scenarios, exact_k=exact_k
                )
    
            if not scenarios:
                st.warning("No feasible scenarios found. Try increasing budget or reducing K.")
            else:
                for i, sc in enumerate(scenarios, start=1):
                    st.subheader(f"Scenario #{i}")
                    st.dataframe(sc, use_container_width=True)



        # # ---------- GOOGLE SHEETS ----------
        # sheet_url_raw = "https://docs.google.com/spreadsheets/d/1jMo9lFTxif0uwAgwJeyn60_E2jM9n5Ku/gviz/tq?tqx=out:csv"
        # sheet_url_off = "https://docs.google.com/spreadsheets/d/1Fst4_Ac4SwmY4WQ1S_rzXSgmrxDb3jvp/gviz/tq?tqx=out:csv"
        # sheet_url_full = "https://docs.google.com/spreadsheets/d/1f7x4teD3iBeFfhmpObHqcj8wl_DkipLwa_JxAO5sYp8/gviz/tq?tqx=out:csv"
    
        # @st.cache_data
        # def load_google_sheets(url):
        #     df = pd.read_csv(url)
        #     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        #     return df
        # if st.button('🔄 Refresh Data'):
        #     st.cache_data.clear()
    
        # df = load_google_sheets(sheet_url_raw)
        # df_coff = load_google_sheets(sheet_url_off)
        # df_full = load_google_sheets(sheet_url_full)
    
        # st.title("💰 Influencer Performance")
        
        # # st.write("🧾 Available columns:", df_full.columns.tolist())
        # # with st.expander("📋 Influencer Data from Google Sheets"):
        # #     st.dataframe(df_full, use_container_width=True)
        
        # # --------------------- Tier Selection ---------------------
        # all_tiers = ['All', 'VIP', 'Mega', 'Mid', 'Macro', 'Micro', 'Nano']
        
        # if 'tier_selection' not in st.session_state:
        #     st.session_state.tier_selection = ['All']
        
        # def update_tiers():
        #     selected = st.session_state['tier_multiselect']
        #     if 'All' in selected:
        #         st.session_state.tier_selection = ['All']
        #     else:
        #         st.session_state.tier_selection = selected
        
        # tier_selection = st.multiselect(
        #     "🏷️ Tier Selection",
        #     options=all_tiers,
        #     default=st.session_state.tier_selection,
        #     key='tier_multiselect',
        #     on_change=update_tiers
        # )
        
        # if 'All' in st.session_state.tier_selection:
        #     filtered_tiers = None
        # else:
        #     filtered_tiers = [t.lower() for t in st.session_state.tier_selection]
        
        # # --------------------- Platform Selection (new) ---------------------
        # platform_column_exists = 'platform' in df_full.columns
        # if platform_column_exists:
        #     platforms_raw = (
        #         df_full['platform']
        #         .astype(str)
        #         .str.strip()
        #         .replace({'nan': '', 'None': '', 'NaN': ''})
        #     )
        #     unique_platforms = sorted([p for p in platforms_raw.unique().tolist() if p])
        #     all_platforms = ['All'] + unique_platforms
        # else:
        #     all_platforms = ['All']  # fallback
        
        # if 'platform_selection' not in st.session_state:
        #     st.session_state.platform_selection = ['All']
        
        # def update_platforms():
        #     selected = st.session_state['platform_multiselect']
        #     if 'All' in selected:
        #         st.session_state.platform_selection = ['All']
        #     else:
        #         st.session_state.platform_selection = selected
        
        # if platform_column_exists:
        #     platform_selection = st.multiselect(
        #         "🖥️ Platform Selection",
        #         options=all_platforms,
        #         default=st.session_state.platform_selection,
        #         key='platform_multiselect',
        #         on_change=update_platforms
        #     )
        # else:
        #     st.info("No 'platform' column found; platform filtering is disabled.")
        #     platform_selection = ['All']
        
        # if 'All' in st.session_state.platform_selection or not platform_column_exists:
        #     filtered_platforms = None
        # else:
        #     filtered_platforms = [p.lower() for p in st.session_state.platform_selection]
        
        # # --------------------- KPI Mapping ---------------------
        # kpi_map = {
        #     'total_impression': 'impression',
        #     'total_engagement': 'engagement',
        #     'total_view': 'view',
        # }
        
        # # --------------------- Helper Functions ---------------------
        # def prepare_df(df_in: pd.DataFrame, kpi_col: str, allowed_tiers=None, allowed_platforms=None) -> pd.DataFrame:
        #     df_work = df_in.copy()
        
        #     # Ensure required columns exist
        #     for col in ['cost', 'impression', 'engagement', 'view', 'tier', 'platform']:
        #         if col not in df_work.columns:
        #             df_work[col] = pd.NA
        
        #     # Tier filter
        #     if allowed_tiers is not None:
        #         df_work = df_work[df_work['tier'].astype(str).str.lower().isin(allowed_tiers)]
        
        #     # Platform filter
        #     if allowed_platforms is not None:
        #         df_work = df_work[df_work['platform'].astype(str).str.lower().isin(allowed_platforms)]
        
        #     # Coerce numeric cols
        #     for col in ['cost', 'impression', 'engagement', 'view']:
        #         df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
        
        #     # Valid rows for cost and kpi
        #     df_work = df_work[df_work['cost'].notna() & (df_work['cost'] > 0)]
        #     df_work = df_work[df_work[kpi_col].notna()]
        #     df_work = df_work.reset_index(drop=True)
        
        #     return df_work
        
        # def summarize_selection(df_sel: pd.DataFrame) -> pd.DataFrame:
        #     if df_sel is None or df_sel.empty:
        #         return pd.DataFrame()
        #     summary = {
        #         'kol_name': 'TOTAL' if 'kol_name' in df_sel.columns else '',
        #         'platform': '',
        #         'cost': df_sel['cost'].sum() if 'cost' in df_sel else 0,
        #         'impression': df_sel['impression'].sum() if 'impression' in df_sel else 0,
        #         'engagement': df_sel['engagement'].sum() if 'engagement' in df_sel else 0,
        #         'view': df_sel['view'].sum() if 'view' in df_sel else 0,
        #         'followers': '' if 'followers' in df_sel.columns else '',
        #         'tier': '',
        #         'score': ''
        #     }
        #     return pd.concat([df_sel, pd.DataFrame([summary])], ignore_index=True)
        
        # # --------------------- Greedy (single) ---------------------
        # def select_kols_greedy(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None):
        #     df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms)
        #     if df_work.empty:
        #         return pd.DataFrame()
        
        #     df_work['score'] = df_work[kpi_col] / df_work['cost']
        #     df_work = df_work.sort_values('score', ascending=False).reset_index(drop=True)
        
        #     selected_rows = []
        #     total_cost = 0.0
        
        #     for _, row in df_work.iterrows():
        #         if len(selected_rows) >= k:
        #             break
        #         if total_cost + row['cost'] <= budget:
        #             selected_rows.append(row)
        #             total_cost += row['cost']
        
        #     result = pd.DataFrame(selected_rows)
        #     return summarize_selection(result)
        
        # # --------------------- Greedy (multiple portfolios for same K) ---------------------
        # def greedy_multiple_scenarios(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, num_scenarios=5):
        #     df_base = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms)
        #     if df_base.empty:
        #         return []
        
        #     scenarios = []
        #     excluded_idx = set()
        
        #     for s in range(num_scenarios):
        #         work = df_base.copy()
        #         if excluded_idx:
        #             work = work[~work.index.isin(excluded_idx)].reset_index(drop=True)
        #             if work.empty:
        #                 break
        
        #         # Compute score and sort
        #         work['score'] = work[kpi_col] / work['cost']
        #         work = work.sort_values('score', ascending=False)
        
        #         # Greedy selection on 'work'
        #         selected_indices = []
        #         selected_rows = []
        #         total_cost = 0.0
        
        #         for i, row in work.iterrows():
        #             if len(selected_rows) >= k:
        #                 break
        #             if total_cost + row['cost'] <= budget:
        #                 selected_rows.append(row)
        #                 selected_indices.append(i)
        #                 total_cost += row['cost']
        
        #         if not selected_rows:
        #             break
        
        #         scenario_df = summarize_selection(pd.DataFrame(selected_rows))
        #         scenarios.append(scenario_df)
        
        #         # Diversify: exclude the highest-score item among the chosen in this scenario
        #         work_chosen = work.loc[selected_indices].copy().sort_values('score', ascending=False)
        #         if not work_chosen.empty:
        #             key_cols = [c for c in ['kol_name', 'platform', 'cost'] if c in df_base.columns]
        #             if key_cols:
        #                 key_vals = tuple(work_chosen.iloc[0][key_cols].tolist())
        #                 mask = pd.Series([True] * len(df_base))
        #                 for c, v in zip(key_cols, key_vals):
        #                     mask &= (df_base[c] == v)
        #                 idx_to_exclude = df_base[mask].index.tolist()
        #                 if idx_to_exclude:
        #                     excluded_idx.add(idx_to_exclude[0])
        #             else:
        #                 excluded_idx.add(work_chosen.index[0])
        
        #     return scenarios
        
        # # --------------------- LP (single) ---------------------
        # def optimize_kols_lp_single(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, exact_k=False):
        #     try:
        #         from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        #     except Exception:
        #         st.error("PuLP not installed. Please install with: pip install pulp")
        #         return pd.DataFrame()
        
        #     df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms)
        #     if df_work.empty:
        #         return pd.DataFrame()
        
        #     # Cap candidates for speed
        #     if len(df_work) > 200:
        #         df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
        
        #     n = len(df_work)
        #     prob = LpProblem("KOL_Selection", LpMaximize)
        #     x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(n)]
        
        #     prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
        #     prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
        #     if exact_k:
        #         prob += lpSum(x[i] for i in range(n)) == k
        #     else:
        #         prob += lpSum(x[i] for i in range(n)) <= k
        
        #     status = prob.solve()
        #     try:
        #         if LpStatus[status] != 'Optimal':
        #             return pd.DataFrame()
        #     except Exception:
        #         pass
        
        #     chosen_idx = [i for i in range(n) if x[i].varValue == 1]
        #     result = df_work.loc[chosen_idx].copy()
        #     return summarize_selection(result)
        
        # # --------------------- LP (multiple portfolios for same K) ---------------------
        # def optimize_kols_lp_multiple(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, num_scenarios=5, exact_k=False):
        #     try:
        #         from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        #     except Exception:
        #         st.error("PuLP not installed. Please install with: pip install pulp")
        #         return []
        
        #     df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms)
        #     if df_work.empty:
        #         return []
        
        #     # Cap candidates for speed
        #     if len(df_work) > 200:
        #         df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
        
        #     n = len(df_work)
        #     scenarios = []
        #     cuts = []  # sets of chosen indices
        
        #     for s in range(num_scenarios):
        #         prob = LpProblem(f"KOL_Selection_{s+1}", LpMaximize)
        #         x = [LpVariable(f"x_{i}_{s}", cat=LpBinary) for i in range(n)]
        
        #         prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
        #         prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
        #         if exact_k:
        #             prob += lpSum(x[i] for i in range(n)) == k
        #         else:
        #             prob += lpSum(x[i] for i in range(n)) <= k
        
        #         # No-good cuts to enforce diversity
        #         for sel_set in cuts:
        #             prob += lpSum(x[i] for i in sel_set) <= max(0, len(sel_set) - 1)
        
        #         status = prob.solve()
        #         try:
        #             if LpStatus[status] != 'Optimal':
        #                 break
        #         except Exception:
        #             pass
        
        #         chosen_idx = [i for i in range(n) if x[i].varValue == 1]
        #         if not chosen_idx:
        #             break
        
        #         cuts.append(set(chosen_idx))
        #         scenarios.append(summarize_selection(df_work.loc[chosen_idx].copy()))
        
        #     return scenarios
        
        # # --------------------- Optimizer UI ---------------------
        # st.header("🎯 KOL Selection Optimizer")
        
        # col1, col2, col3 = st.columns([1, 1, 1])
        # with col1:
        #     selection_mode = st.radio("🔀 Optimization Method", ["Greedy", "Linear Programming"], horizontal=False)
        # with col2:
        #     budget = st.number_input("💰 Total Budget (THB)", min_value=0, value=250000, step=1000)
        # with col3:
        #     kpi_option = st.selectbox("📊 KPI Focus", options=['total_impression', 'total_engagement', 'total_view'])
        
        # kpi_col = kpi_map[kpi_option]
        
        # st.subheader("🧪 Scenario Mode")
        # scenario_mode = st.radio("Choose scenario mode", ["By K values", "Multiple portfolios (same K)"], horizontal=True)
        
        # # Inputs per scenario mode
        # if scenario_mode == "By K values":
        #     k_values_str = st.text_input("Enter K values (comma-separated)", value="2,3,5")
        #     try:
        #         k_values = [int(x.strip()) for x in k_values_str.split(",") if x.strip().isdigit()]
        #     except Exception:
        #         k_values = []
        #     exact_k = False
        #     if selection_mode == "Linear Programming":
        #         exact_k = st.checkbox("Force exactly K KOLs (LP only)", value=False, help="If off, LP may choose fewer KOLs if the budget is too tight.")
        # else:
        #     fixed_k = st.number_input("🔢 Number of KOLs (K)", min_value=1, value=5, step=1)
        #     num_scenarios = st.number_input("How many scenarios?", min_value=2, value=5, step=1)
        #     exact_k = False
        #     if selection_mode == "Linear Programming":
        #         exact_k = st.checkbox("Force exactly K KOLs (LP only)", value=False)
        
        # # --------------------- Run Optimization ---------------------
        # if st.button("🚀 Run Optimization"):
        #     allowed_tiers = filtered_tiers
        #     allowed_platforms = filtered_platforms
        
        #     if scenario_mode == "By K values":
        #         if not k_values:
        #             st.warning("Please provide at least one valid K.")
        #         else:
        #             st.success("✅ Optimization complete!")
        #             for k in k_values:
        #                 st.subheader(f"Scenario: best portfolio for K = {k}")
        #                 if selection_mode == "Greedy":
        #                     res = select_kols_greedy(df_full, budget, k, kpi_col, allowed_tiers, allowed_platforms)
        #                 else:
        #                     res = optimize_kols_lp_single(df_full, budget, k, kpi_col, allowed_tiers, allowed_platforms, exact_k=exact_k)
        #                 if res.empty:
        #                     st.info("No feasible selection under budget.")
        #                 else:
        #                     st.dataframe(res, use_container_width=True)
        #     else:
        #         st.success("✅ Optimization complete!")
        #         if selection_mode == "Greedy":
        #             scenarios = greedy_multiple_scenarios(
        #                 df_full, budget, fixed_k, kpi_col, allowed_tiers, allowed_platforms, num_scenarios=num_scenarios
        #             )
        #         else:
        #             scenarios = optimize_kols_lp_multiple(
        #                 df_full, budget, fixed_k, kpi_col, allowed_tiers, allowed_platforms,
        #                 num_scenarios=num_scenarios, exact_k=exact_k
        #             )
        
        #         if not scenarios:
        #             st.warning("No feasible scenarios found. Try increasing budget or reducing K.")
        #         else:
        #             for i, sc in enumerate(scenarios, start=1):
        #                 st.subheader(f"Scenario #{i}")
        #                 st.dataframe(sc, use_container_width=True)


# ---------- PAGE 3: SUMMARY BUDGET ----------
elif st.session_state.page == "Optimized Budget":
    # ---------- Compatibility rerun wrapper ----------
    def _rerun():
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()

    # --------- Config ---------
    TIERS = ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']
    DISPLAY_ORDER = ['Nano', 'Micro', 'Mid', 'Macro', 'Mega', 'VIP']  # display stack order
    BIG_MAX = 1_000_000_000.0  # default max for min-budget mode
    KPI_CANON = ['Impression','View','Engagement','Share','CPE','CPShare']

    # --------- Custom Errors ---------
    class NotEnoughDataError(Exception):
        pass

    # --------- Helpers ---------
    def _validate_and_prepare_weights(df):
        required_cols = {'Category', 'Tier', 'KPI', 'Weights'}
        if df is None:
            raise ValueError("weights_df not provided.")
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"weights_df missing columns: {missing}")

        df = df.copy()
        for col in ['Category', 'Tier', 'KPI']:
            df[col] = df[col].astype(str).str.strip()

        # Platform optional
        if 'Platform' not in df.columns:
            df['Platform'] = ''
        df['Platform'] = df['Platform'].astype(str).str.strip()

        df['Weights'] = pd.to_numeric(df['Weights'], errors='coerce')
        if df['Weights'].isna().any():
            raise ValueError("Found non-numeric or missing Weights in weights_df.")

        # Canonicalize KPI names (add Share, CPE, CPShare)
        kpi_map = {
            'impression': 'Impression', 'impressions': 'Impression', 'imp': 'Impression',
            'view': 'View', 'views': 'View',
            'engagement': 'Engagement', 'eng': 'Engagement',
            'share': 'Share', 'shares': 'Share',
            'cpe': 'CPE', 'cost per engagement': 'CPE',
            'cpshare': 'CPShare', 'cp share': 'CPShare', 'cost per share': 'CPShare'
        }
        df['KPI'] = df['KPI'].str.lower().map(kpi_map).fillna(df['KPI'])
        return df

    def _platform_set(series):
        return sorted({str(x).strip() for x in series if str(x).strip() != ''})

    def _get_weights_for_kpi_lenient(df, category, kpi, agg='sum'):
        """
        Lenient loader used for optimization and reporting:
          - Aggregates across available platforms to Tier-level weights.
          - Missing tiers/platform pairs are filled as 0.0 (we still run).
          - Returns (weights_map, warning_message_or_None, has_any_weights_bool).
        If there are no usable weights at all, has_any=False and a warning explains it.
        """
        sub = df[(df['Category'] == category) & (df['KPI'] == kpi)]
        mp = {t: 0.0 for t in TIERS}

        if sub.empty:
            warn = f"No rows for KPI='{kpi}' in Category='{category}'."
            return mp, warn, False

        platforms = _platform_set(sub['Platform'])
        # Find missing tiers and tier-platform pairs
        missing_tiers = []
        missing_pairs = []
        for t in TIERS:
            t_sub = sub[sub['Tier'] == t]
            if t_sub.empty:
                missing_tiers.append(t)
            else:
                if platforms:
                    present_p = {str(p).strip() for p in t_sub['Platform']}
                    for p in platforms:
                        if p not in present_p:
                            missing_pairs.append((t, p))

        # Aggregate across platforms for existing data
        grouped = sub.groupby('Tier', as_index=False)['Weights'].agg(agg)
        for _, row in grouped.iterrows():
            t = str(row['Tier']).strip()
            if t in mp:
                mp[t] = float(row['Weights'])

        has_any = any(v != 0.0 for v in mp.values())

        warn_parts = []
        if missing_tiers:
            warn_parts.append("missing tiers: " + ", ".join(missing_tiers))
        if missing_pairs:
            warn_parts.append("missing tier-platform pairs: " + ", ".join([f"{t}/{p}" for t, p in missing_pairs]))

        warn = None
        if warn_parts:
            warn = f"Partial coverage for KPI='{kpi}' in Category='{category}' (" + "; ".join(warn_parts) + "). Proceeding with zeros for missing items."
        if not has_any:
            warn = f"No usable weights for KPI='{kpi}' in Category='{category}'."
        return mp, warn, has_any

    def _gather_kpi_maps_with_warnings(df, category, kpis=KPI_CANON):
        maps = {}
        warns = []
        for k in kpis:
            m, w, _ = _get_weights_for_kpi_lenient(df, category, k)
            maps[k] = m
            if w:
                warns.append(w)
        # dedupe warnings while preserving order
        warns = list(dict.fromkeys([w for w in warns if w]))
        return maps, warns

    def _build_weights_vector_for_priority_lenient(df, category, priority):
        """
        Returns: weights_vec, used_kpis, warnings_list
        - balanced: average of Impression/View/Engagement (lenient, with warnings)
        - single KPI (incl. Share/CPE/CPShare): that KPI (lenient, with warning)
        If all contributing KPIs have no usable weights, raises NotEnoughDataError.
        """
        p = str(priority).strip().lower()
        warnings = []
        used = []

        if p == 'balanced':
            imap, iwarn, iok = _get_weights_for_kpi_lenient(df, category, 'Impression')
            vmap, vwarn, vok = _get_weights_for_kpi_lenient(df, category, 'View')
            emap, ewarn, eok = _get_weights_for_kpi_lenient(df, category, 'Engagement')
            if iwarn: warnings.append(iwarn)
            if vwarn: warnings.append(vwarn)
            if ewarn: warnings.append(ewarn)

            if not (iok or vok or eok):
                raise NotEnoughDataError(f"No usable weights for Impressions, Views, or Engagement in Category='{category}'.")
            w = [ (imap[t] + vmap[t] + emap[t]) / 3.0 for t in TIERS ]
            used = ['Impression', 'View', 'Engagement']
            return np.array(w, float), used, [w for w in warnings if w]
        else:
            kpi_map = {
                'impression':'Impression','impressions':'Impression','imp':'Impression',
                'view':'View','views':'View',
                'engagement':'Engagement','eng':'Engagement',
                'share':'Share','cpe':'CPE','cpshare':'CPShare'
            }
            kpi_key = kpi_map.get(p, p)
            mp, warn, ok = _get_weights_for_kpi_lenient(df, category, kpi_key)
            if warn: warnings.append(warn)
            if not ok:
                raise NotEnoughDataError(warn or f"No usable weights for KPI='{kpi_key}' in Category='{category}'.")
            w = [ mp[t] for t in TIERS ]
            used = [kpi_key]
            return np.array(w, float), used, [w for w in warnings if w]

    def _compute_named_scores(x, kpi_maps):
        # kpi_maps: dict name -> {tier -> weight}
        def dot(w_map):
            return float(sum(x[i] * w_map.get(TIERS[i], 0.0) for i in range(len(TIERS))))
        return {name: dot(wmap) for name, wmap in kpi_maps.items()}

    def _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=None, b_ub=None):
        n = len(TIERS)
        A_eq = [np.ones(n)]
        b_eq = [total_budget]
        bounds = [(min_alloc[t], max_alloc[t]) for t in TIERS]
        return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    def _solve_lp_general(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None):
        return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    def _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category):
        weights_vec, used_kpis, warns = _build_weights_vector_for_priority_lenient(df, category, priority)
        res = _solve_lp(-weights_vec, total_budget, min_alloc, max_alloc)
        if not res.success:
            return None, warns

        # Build maps for all KPIs (for reporting)
        kpi_maps, warn_all = _gather_kpi_maps_with_warnings(df, category, KPI_CANON)
        warns.extend(warn_all)

        scores = _compute_named_scores(res.x, kpi_maps)
        return dict(
            x=res.x,
            weights_vec=weights_vec,
            used_kpis=used_kpis,
            primary_score=float(np.dot(res.x, weights_vec)),
            kpi_maps=kpi_maps,      # for reuse when packing scenarios
            scores=scores           # scores for optimal
        ), list(dict.fromkeys([w for w in warns if w]))

    def get_five_budget_scenarios(weights_df, total_budget, min_alloc, max_alloc, priority='balanced', category='Total IPG'):
        warnings = []
        invalid = [t for t in TIERS if t not in min_alloc or t not in max_alloc]
        if invalid:
            raise ValueError(f"Missing bounds for tiers: {invalid}")
        if any(min_alloc[t] > max_alloc[t] for t in TIERS):
            raise ValueError("Min > Max for some tiers.")
        if sum(min_alloc[t] for t in TIERS) > total_budget:
            raise ValueError("Sum of minimums exceeds total budget.")

        df = _validate_and_prepare_weights(weights_df)
        base, warns = _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category)
        warnings.extend(warns or [])
        if base is None:
            return [], warnings

        x_star = base['x']
        weights_vec = base['weights_vec']
        z_star = base['primary_score']
        kpi_maps = base['kpi_maps']

        def pack(label, x_vec):
            alloc = {TIERS[i]: float(x_vec[i]) for i in range(len(TIERS))}
            scores = _compute_named_scores(x_vec, kpi_maps)
            return dict(
                label=label,
                allocation=alloc,
                primary_score=float(np.dot(x_vec, weights_vec)),
                scores=scores
            )

        scenarios = [pack("Optimal", x_star)]

        # KPI tolerance to diversify (fixed 1.5%)
        eps_abs = abs(z_star) * 0.015
        A_ub = [-weights_vec]; b_ub = [-(z_star - eps_abs)]

        for i, t in enumerate(TIERS):
            c = np.zeros(len(TIERS)); c[i] = -1.0
            res = _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=A_ub, b_ub=b_ub)
            if res.success:
                scenarios.append(pack(f"Near-optimal (emphasize {t})", res.x))

        def key(s): return tuple(round(s['allocation'][t], 2) for t in TIERS)
        uniq = {}
        for s in scenarios:
            uniq.setdefault(key(s), s)
        out = list(uniq.values())
        out.sort(key=lambda s: s['primary_score'], reverse=True)
        return out[:5], warnings

    def get_five_target_scenarios(weights_df, target_value, kpi_type, min_alloc, max_alloc, category='Total IPG', epsilon_pct=1.5):
        warnings = []
        invalid = [t for t in TIERS if t not in min_alloc or t not in max_alloc]
        if invalid:
            raise ValueError(f"Missing bounds: {invalid}")
        if any(min_alloc[t] > max_alloc[t] for t in TIERS):
            raise ValueError("Min > Max for some tiers.")

        df = _validate_and_prepare_weights(weights_df)

        # Canonicalize KPI name
        kpi_map = {
            'impression': 'Impression', 'impressions': 'Impression', 'imp': 'Impression',
            'view': 'View', 'views': 'View',
            'engagement': 'Engagement', 'eng': 'Engagement',
            'share': 'Share', 'cpe': 'CPE', 'cpshare': 'CPShare'
        }
        kpi_key = kpi_map.get(str(kpi_type).lower(), kpi_type)

        # Lenient load with warnings; stop only if no usable weights
        w_map, warn, ok = _get_weights_for_kpi_lenient(df, category, kpi_key)
        if warn: warnings.append(warn)
        if not ok:
            raise NotEnoughDataError(warn or f"No usable weights for KPI='{kpi_key}' in Category='{category}'.")

        # Feasibility check
        max_possible = sum(float(max_alloc[t]) * w_map.get(t, 0.0) for t in TIERS)
        if float(target_value) > max_possible + 1e-9:
            return [], warnings

        n = len(TIERS)
        # Minimize total budget s.t. KPI >= target
        c = np.ones(n, float)
        A_ub = [np.array([-w_map[t] for t in TIERS], float)]
        b_ub = [-float(target_value)]
        bounds = [(float(min_alloc[t]), float(max_alloc[t])) for t in TIERS]
        res = _solve_lp_general(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
        if not res.success:
            return [], warnings

        x_star = res.x
        B_star = float(np.sum(x_star))
        B_cap = B_star * (1 + float(epsilon_pct)/100.0)

        # Collect maps for all KPIs for reporting
        kpi_maps, warn_all = _gather_kpi_maps_with_warnings(df, category, KPI_CANON)
        warnings.extend(warn_all)

        def pack(label, x):
            alloc = {TIERS[i]: float(x[i]) for i in range(n)}
            scores = _compute_named_scores(x, kpi_maps)
            achieved_target_kpi = float(sum(x[i] * w_map.get(TIERS[i], 0.0) for i in range(n)))
            return dict(
                label=label,
                allocation=alloc,
                required_budget=float(np.sum(x)),
                target_kpi_name=kpi_key,
                target_kpi_value=achieved_target_kpi,
                scores=scores
            )

        scenarios = [pack("Target-Optimal (min budget)", x_star)]

        # Near-min variations under budget cap and KPI >= target
        A_ub2 = [
            np.array([-w_map[t] for t in TIERS], float),  # KPI >= target
            np.ones(n, float)                             # Budget <= B_cap
        ]
        b_ub2 = [-float(target_value), float(B_cap)]

        for i, t in enumerate(TIERS):
            c2 = np.zeros(n, float); c2[i] = -1.0
            res2 = _solve_lp_general(c2, A_ub=A_ub2, b_ub=b_ub2, bounds=bounds)
            if res2.success:
                scenarios.append(pack(f"Near-min (emphasize {t})", res2.x))

        def key(s): return tuple(round(s['allocation'][t], 2) for t in TIERS)
        uniq = {}
        for s in scenarios:
            uniq.setdefault(key(s), s)
        out = list(uniq.values())
        out.sort(key=lambda s: (s.get('required_budget', 0.0), -s['scores'].get(kpi_key, 0.0)))
        return out[:5], list(dict.fromkeys([w for w in warnings if w]))

    # --------- UI ---------
    st.title("Budget Optimization Tool")

    # Mode selector at top
    mode = st.radio("Select optimization mode:", ["Maximize KPI (given budget)", "Achieve KPI target (min budget)"])

    # Clear state on mode change to avoid carry-over
    if 'mode_prev' not in st.session_state:
        st.session_state.mode_prev = mode
    elif mode != st.session_state.mode_prev:
        for k in list(st.session_state.keys()):
            if k.endswith('_max') or k.endswith('_tgt') or k.startswith('result_'):
                try:
                    del st.session_state[k]
                except KeyError:
                    pass
        st.session_state.mode_prev = mode
        _rerun()

    # Data check
    if 'weights_df' not in globals():
        st.error("weights_df not found. Load it into a DataFrame named 'weights_df'.")
        st.stop()

    try:
        df_clean = _validate_and_prepare_weights(weights_df)
    except Exception as e:
        st.error(str(e))
        st.stop()

    # Category (common)
    cats = sorted(df_clean['Category'].dropna().unique().tolist())
    default_idx = cats.index("Total IPG") if "Total IPG" in cats else 0
    category = st.selectbox("Select Category:", options=cats, index=default_idx)

    # Helper for styling: highlight max in each numeric column
    def _highlight_max(s):
        try:
            max_val = s.max()
            return ['background-color: #d1ffd6; font-weight: 700' if v == max_val else '' for v in s]
        except Exception:
            return [''] * len(s)

    if mode == "Maximize KPI (given budget)":
        total_budget = st.number_input("Total Budget", min_value=0.0, value=10000.0, step=100.0, key="total_budget_max")

        # Priority now includes Share, CPE, CPShare
        priority = st.selectbox(
            "Optimization Priority",
            ["balanced", "impressions", "views", "engagement", "share", "cpe", "cpshare"],
            key="priority_max"
        )

        with st.expander("Advanced constraints (per-tier min/max)", expanded=False):
            col1, col2 = st.columns(2)
            min_alloc, max_alloc = {}, {}
            with col1:
                st.subheader("Minimum Allocation")
                for t in TIERS:
                    min_alloc[t] = st.number_input(f"Min {t}", min_value=0.0, value=0.0, step=100.0, key=f"min_{t}_max")
            with col2:
                st.subheader("Maximum Allocation")
                for t in TIERS:
                    max_alloc[t] = st.number_input(f"Max {t}", min_value=0.0, value=float(total_budget), step=100.0, key=f"max_{t}_max")

        if st.button("Generate 5 scenarios", key="run_max"):
            if any(min_alloc[t] > max_alloc[t] for t in TIERS):
                st.error("Infeasible: some Min > Max.")
                st.stop()
            if sum(min_alloc[t] for t in TIERS) > total_budget:
                st.error("Infeasible: sum of minimums exceeds total budget.")
                st.stop()

            try:
                scenarios, warns = get_five_budget_scenarios(
                    weights_df=weights_df,
                    total_budget=float(total_budget),
                    min_alloc={k: float(v) for k, v in min_alloc.items()},
                    max_alloc={k: float(v) for k, v in max_alloc.items()},
                    priority=priority,
                    category=category
                )
                for w in (warns or []):
                    st.warning(w)
            except NotEnoughDataError as e:
                st.warning("We don't have enough data to optimize for this selection. " + str(e))
                st.stop()
            except Exception as e:
                st.exception(e)
                st.stop()

            if not scenarios:
                st.error("No feasible scenarios.")
            else:
                st.success("Generated scenarios.")
                scenario_ids = [f"Scenario {i+1}" for i in range(len(scenarios))]
                recs = []
                for i, s in enumerate(scenarios):
                    for tier in DISPLAY_ORDER:
                        recs.append({"Scenario": scenario_ids[i], "Tier": tier, "Allocation": float(s['allocation'].get(tier, 0.0))})
                chart_df = pd.DataFrame(recs)
                chart_df["TierOrder"] = chart_df["Tier"].map({t:i for i,t in enumerate(DISPLAY_ORDER)})

                chart = (
                    alt.Chart(chart_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Scenario:N", sort=scenario_ids),
                        y=alt.Y("Allocation:Q", stack="zero", title="Allocation"),
                        color=alt.Color("Tier:N", sort=DISPLAY_ORDER, scale=alt.Scale(domain=DISPLAY_ORDER)),
                        order=alt.Order("TierOrder:Q"),
                        tooltip=[alt.Tooltip("Scenario:N"), alt.Tooltip("Tier:N"), alt.Tooltip("Allocation:Q", format=",.2f")]
                    ).properties(height=420)
                )
                st.altair_chart(chart, use_container_width=True)

                # Build KPI table with 6 KPIs; highlight max per column; exclude Total KPI
                rows = []
                for i, s in enumerate(scenarios):
                    sc = s['scores']
                    rows.append({
                        "Scenario": scenario_ids[i],
                        "Priority KPI Score": s['primary_score'],
                        "Impressions": sc.get('Impression', 0.0),
                        "Views": sc.get('View', 0.0),
                        "Engagement": sc.get('Engagement', 0.0),
                        "Share": sc.get('Share', 0.0),
                        "CPE": sc.get('CPE', 0.0),
                        "CPShare": sc.get('CPShare', 0.0),
                    })
                kpi_df = pd.DataFrame(rows)

                fmt = {
                    "Priority KPI Score":"{:,.2f}",
                    "Impressions":"{:,.2f}",
                    "Views":"{:,.2f}",
                    "Engagement":"{:,.2f}",
                    "Share":"{:,.2f}",
                    "CPE":"{:,.2f}",
                    "CPShare":"{:,.2f}",
                }
                highlight_cols = ["Priority KPI Score","Impressions","Views","Engagement","Share","CPE","CPShare"]
                st.dataframe(
                    kpi_df.style
                    .format(fmt)
                    .apply(_highlight_max, subset=highlight_cols),
                    hide_index=True, use_container_width=True
                )

    else:
        # Min budget mode with expanded KPI choices
        kpi_type = st.selectbox(
            "KPI to target",
            ["impressions", "views", "engagement", "share", "cpe", "cpshare"],
            key="kpi_tgt"
        )
        target_value = st.number_input(f"Target {kpi_type.title()}", min_value=0.0, value=1_000_000.0, step=1000.0, key="target_value_tgt")

        with st.expander("Advanced constraints (per-tier min/max)", expanded=True):
            col1, col2 = st.columns(2)
            min_alloc, max_alloc = {}, {}
            with col1:
                st.subheader("Minimum Allocation")
                for t in TIERS:
                    min_alloc[t] = st.number_input(f"Min {t}", min_value=0.0, value=0.0, step=100.0, key=f"min_{t}_tgt")
            with col2:
                st.subheader("Maximum Allocation")
                for t in TIERS:
                    max_alloc[t] = st.number_input(f"Max {t}", min_value=0.0, value=BIG_MAX, step=100.0, key=f"max_{t}_tgt")

        if st.button("Generate 5 scenarios to achieve KPI", key="run_tgt_free"):
            try:
                scenarios, warns = get_five_target_scenarios(
                    weights_df=weights_df,
                    target_value=float(target_value),
                    kpi_type=kpi_type,
                    min_alloc=min_alloc, max_alloc=max_alloc,
                    category=category
                )
                for w in (warns or []):
                    st.warning(w)
            except NotEnoughDataError as e:
                st.warning("We don't have enough data to optimize for this selection. " + str(e))
                st.stop()
            except Exception as e:
                st.exception(e)
                st.stop()

            if not scenarios:
                st.error("No feasible scenarios for the given target and constraints.")
            else:
                st.success("Generated scenarios.")
                scenario_ids = [f"Scenario {i+1}" for i in range(len(scenarios))]
                recs = []
                for i, s in enumerate(scenarios):
                    for tier in DISPLAY_ORDER:
                        recs.append({"Scenario": scenario_ids[i], "Tier": tier, "Allocation": float(s['allocation'].get(tier, 0.0))})
                chart_df = pd.DataFrame(recs)
                chart_df["TierOrder"] = chart_df["Tier"].map({t:i for i,t in enumerate(DISPLAY_ORDER)})

                chart = (
                    alt.Chart(chart_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Scenario:N", sort=scenario_ids),
                        y=alt.Y("Allocation:Q", stack="zero", title="Allocation (Budget)"),
                        color=alt.Color("Tier:N", sort=DISPLAY_ORDER, scale=alt.Scale(domain=DISPLAY_ORDER)),
                        order=alt.Order("TierOrder:Q"),
                        tooltip=[alt.Tooltip("Scenario:N"), alt.Tooltip("Tier:N"), alt.Tooltip("Allocation:Q", format=",.2f")]
                    ).properties(height=420)
                )
                st.altair_chart(chart, use_container_width=True)

                # KPI table for target mode: include 6 KPIs, plus Required Budget and Target KPI fields
                rows = []
                for i, s in enumerate(scenarios):
                    sc = s['scores']
                    rows.append({
                        "Scenario": scenario_ids[i],
                        "Required Budget": s['required_budget'],
                        "Target KPI": s['target_kpi_name'],
                        "Target KPI Achieved": s['target_kpi_value'],
                        "Impressions": sc.get('Impression', 0.0),
                        "Views": sc.get('View', 0.0),
                        "Engagement": sc.get('Engagement', 0.0),
                        "Share": sc.get('Share', 0.0),
                        "CPE": sc.get('CPE', 0.0),
                        "CPShare": sc.get('CPShare', 0.0),
                    })
                kpi_df = pd.DataFrame(rows)

                fmt = {
                    "Required Budget":"{:,.2f}",
                    "Target KPI Achieved":"{:,.2f}",
                    "Impressions":"{:,.2f}",
                    "Views":"{:,.2f}",
                    "Engagement":"{:,.2f}",
                    "Share":"{:,.2f}",
                    "CPE":"{:,.2f}",
                    "CPShare":"{:,.2f}",
                }
                # Highlight maxima for KPI columns only (not for budget/target fields)
                highlight_cols = ["Impressions","Views","Engagement","Share","CPE","CPShare","Target KPI Achieved"]
                st.dataframe(
                    kpi_df.style
                    .format(fmt)
                    .apply(_highlight_max, subset=highlight_cols),
                    hide_index=True, use_container_width=True
                )

# elif st.session_state.page == "Optimized Budget":
#     # ---------- Compatibility rerun wrapper ----------
#     def _rerun():
#         if hasattr(st, "rerun"):
#             st.rerun()
#         elif hasattr(st, "experimental_rerun"):
#             st.experimental_rerun()
    
#     # --------- Config ---------
#     TIERS = ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']
#     DISPLAY_ORDER = ['Nano', 'Micro', 'Mid', 'Macro', 'Mega', 'VIP']  # display stack order
#     BIG_MAX = 1_000_000_000.0  # default max for min-budget mode
    
#     # --------- Helpers ---------
#     def _validate_and_prepare_weights(df):
#         required_cols = {'Category', 'Tier', 'KPI', 'Weights'}
#         if df is None:
#             raise ValueError("weights_df not provided.")
#         missing = required_cols - set(df.columns)
#         if missing:
#             raise ValueError(f"weights_df missing columns: {missing}")
    
#         df = df.copy()
#         for col in ['Category', 'Tier', 'KPI']:
#             df[col] = df[col].astype(str).str.strip()
#         df['Weights'] = pd.to_numeric(df['Weights'], errors='coerce')
#         if df['Weights'].isna().any():
#             raise ValueError("Found non-numeric or missing Weights in weights_df.")
    
#         kpi_map = {'impression': 'Impression','impressions': 'Impression',
#                    'view': 'View','views': 'View','engagement': 'Engagement'}
#         df['KPI'] = df['KPI'].str.lower().map(kpi_map).fillna(df['KPI'])
#         return df
    
#     def _get_weights_by_kpi(df, category):
#         cat_df = df[df['Category'] == category]
#         if cat_df.empty:
#             raise ValueError(f"No rows found for Category='{category}'.")
#         def to_map(kpi):
#             sub = cat_df[cat_df['KPI'] == kpi]
#             if sub.empty:
#                 raise ValueError(f"No rows for KPI='{kpi}' in Category='{category}'.")
#             mp = sub.set_index('Tier')['Weights'].to_dict()
#             miss = [t for t in TIERS if t not in mp]
#             if miss:
#                 raise ValueError(f"Missing tiers for KPI='{kpi}': {miss}")
#             return mp
#         return to_map('Impression'), to_map('View'), to_map('Engagement')
    
#     def _build_priority_weights(priority, imp_w, view_w, eng_w):
#         p = str(priority).strip().lower()
#         if p == 'impressions':
#             w = [imp_w[t] for t in TIERS]
#         elif p == 'views':
#             w = [view_w[t] for t in TIERS]
#         elif p == 'engagement':
#             w = [eng_w[t] for t in TIERS]
#         else:
#             w = [(imp_w[t] + view_w[t] + eng_w[t]) / 3.0 for t in TIERS]
#         return np.array(w, float)
    
#     def _compute_kpis(x, imp_w, view_w, eng_w):
#         imps = float(sum(x[i] * imp_w[TIERS[i]] for i in range(len(TIERS))))
#         views = float(sum(x[i] * view_w[TIERS[i]] for i in range(len(TIERS))))
#         eng = float(sum(x[i] * eng_w[TIERS[i]] for i in range(len(TIERS))))
#         return imps, views, eng, imps + views + eng
    
#     def _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=None, b_ub=None):
#         n = len(TIERS)
#         A_eq = [np.ones(n)]
#         b_eq = [total_budget]
#         bounds = [(min_alloc[t], max_alloc[t]) for t in TIERS]
#         return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
#     def _solve_lp_general(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None):
#         return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
#     def _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category):
#         imp_w, view_w, eng_w = _get_weights_by_kpi(df, category)
#         weights_vec = _build_priority_weights(priority, imp_w, view_w, eng_w)
#         res = _solve_lp(-weights_vec, total_budget, min_alloc, max_alloc)
#         if not res.success:
#             return None
#         imps, views, eng, total_kpi = _compute_kpis(res.x, imp_w, view_w, eng_w)
#         return dict(
#             x=res.x, weights_vec=weights_vec,
#             impression_w=imp_w, view_w=view_w, engagement_w=eng_w,
#             primary_score=float(np.dot(res.x, weights_vec)),
#             imps=imps, views=views, eng=eng, total_kpi=total_kpi
#         )
    
#     def get_five_budget_scenarios(weights_df, total_budget, min_alloc, max_alloc, priority='balanced', category='Total IPG'):
#         invalid = [t for t in TIERS if t not in min_alloc or t not in max_alloc]
#         if invalid:
#             raise ValueError(f"Missing bounds for tiers: {invalid}")
#         if any(min_alloc[t] > max_alloc[t] for t in TIERS):
#             raise ValueError("Min > Max for some tiers.")
#         if sum(min_alloc[t] for t in TIERS) > total_budget:
#             raise ValueError("Sum of minimums exceeds total budget.")
    
#         df = _validate_and_prepare_weights(weights_df)
#         base = _optimize_primary(df, total_budget, min_alloc, max_alloc, priority, category)
#         if base is None:
#             return []
    
#         x_star = base['x']; weights_vec = base['weights_vec']
#         imp_w, view_w, eng_w = base['impression_w'], base['view_w'], base['engagement_w']
#         z_star = base['primary_score']
    
#         def pack(label, x_vec):
#             alloc = {TIERS[i]: float(x_vec[i]) for i in range(len(TIERS))}
#             imps, views, eng, total_kpi = _compute_kpis(x_vec, imp_w, view_w, eng_w)
#             return dict(label=label, allocation=alloc, impressions=imps, views=views,
#                         engagement=eng, total_kpi=total_kpi,
#                         primary_score=float(np.dot(x_vec, weights_vec)))
    
#         scenarios = [pack("Optimal", x_star)]
    
#         # KPI tolerance to diversify (fixed 1.5%)
#         eps_abs = abs(z_star) * 0.015
#         A_ub = [-weights_vec]; b_ub = [-(z_star - eps_abs)]
    
#         for i, t in enumerate(TIERS):
#             c = np.zeros(len(TIERS)); c[i] = -1.0
#             res = _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=A_ub, b_ub=b_ub)
#             if res.success:
#                 scenarios.append(pack(f"Near-optimal (emphasize {t})", res.x))
    
#         def key(s): return tuple(round(s['allocation'][t], 2) for t in TIERS)
#         uniq = {}
#         for s in scenarios: uniq.setdefault(key(s), s)
#         out = list(uniq.values())
#         out.sort(key=lambda s: s['primary_score'], reverse=True)
#         return out[:5]
    
#     def _kpi_map_for_type(kpi_type, imp_w, view_w, eng_w):
#         kt = str(kpi_type).strip().lower()
#         if kt in ('impression','impressions'): return imp_w, 'Impressions'
#         if kt in ('view','views'): return view_w, 'Views'
#         if kt in ('engagement',): return eng_w, 'Engagement'
#         raise ValueError("kpi_type must be one of: impressions, views, engagement")
    
#     def get_five_target_scenarios(weights_df, target_value, kpi_type, min_alloc, max_alloc, category='Total IPG', epsilon_pct=1.5):
#         # epsilon_pct is fixed internally; no UI
#         invalid = [t for t in TIERS if t not in min_alloc or t not in max_alloc]
#         if invalid: raise ValueError(f"Missing bounds: {invalid}")
#         if any(min_alloc[t] > max_alloc[t] for t in TIERS):
#             raise ValueError("Min > Max for some tiers.")
    
#         df = _validate_and_prepare_weights(weights_df)
#         imp_w, view_w, eng_w = _get_weights_by_kpi(df, category)
#         w_map, _ = _kpi_map_for_type(kpi_type, imp_w, view_w, eng_w)
    
#         max_possible = sum(max_alloc[t] * w_map[t] for t in TIERS)
#         if float(target_value) > max_possible + 1e-9:
#             return []
    
#         n = len(TIERS)
#         # Baseline: minimize total budget s.t. KPI >= target
#         c = np.ones(n, float)
#         A_ub = [np.array([-w_map[t] for t in TIERS], float)]
#         b_ub = [-float(target_value)]
#         bounds = [(float(min_alloc[t]), float(max_alloc[t])) for t in TIERS]
#         res = _solve_lp_general(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
#         if not res.success:
#             return []
    
#         x_star = res.x
#         B_star = float(np.sum(x_star))
#         B_cap = B_star * (1 + float(epsilon_pct)/100.0)
    
#         def pack(label, x):
#             alloc = {TIERS[i]: float(x[i]) for i in range(n)}
#             imps, views, eng, total_kpi = _compute_kpis(x, imp_w, view_w, eng_w)
#             return dict(label=label, allocation=alloc, required_budget=float(np.sum(x)),
#                         impressions=imps, views=views, engagement=eng, total_kpi=total_kpi)
    
#         scenarios = [pack("Target-Optimal (min budget)", x_star)]
    
#         # Near-min variations under budget cap and KPI >= target
#         A_ub2 = [
#             np.array([-w_map[t] for t in TIERS], float),  # KPI >= target
#             np.ones(n, float)                             # Budget <= B_cap
#         ]
#         b_ub2 = [-float(target_value), float(B_cap)]
    
#         for i, t in enumerate(TIERS):
#             c2 = np.zeros(n, float); c2[i] = -1.0
#             res2 = _solve_lp_general(c2, A_ub=A_ub2, b_ub=b_ub2, bounds=bounds)
#             if res2.success:
#                 scenarios.append(pack(f"Near-min (emphasize {t})", res2.x))
    
#         def key(s): return tuple(round(s['allocation'][t], 2) for t in TIERS)
#         uniq = {}
#         for s in scenarios: uniq.setdefault(key(s), s)
#         out = list(uniq.values())
#         out.sort(key=lambda s: (s['required_budget'], -s['total_kpi']))
#         return out[:5]
    
#     # --------- UI ---------
#     st.title("Budget Optimization Tool")
    
#     # Mode selector at top
#     mode = st.radio("Select optimization mode:", ["Maximize KPI (given budget)", "Achieve KPI target (min budget)"])
    
#     # Clear state on mode change to avoid carry-over
#     if 'mode_prev' not in st.session_state:
#         st.session_state.mode_prev = mode
#     elif mode != st.session_state.mode_prev:
#         for k in list(st.session_state.keys()):
#             if k.endswith('_max') or k.endswith('_tgt') or k.startswith('result_'):
#                 try:
#                     del st.session_state[k]
#                 except KeyError:
#                     pass
#         st.session_state.mode_prev = mode
#         _rerun()
    
#     # Data check
#     if 'weights_df' not in globals():
#         st.error("weights_df not found. Load it into a DataFrame named 'weights_df'.")
#         st.stop()
    
#     try:
#         df_clean = _validate_and_prepare_weights(weights_df)
#     except Exception as e:
#         st.error(str(e))
#         st.stop()
    
#     # Category (common)
#     cats = sorted(df_clean['Category'].dropna().unique().tolist())
#     default_idx = cats.index("Total IPG") if "Total IPG" in cats else 0
#     category = st.selectbox("Select Category:", options=cats, index=default_idx)
    
#     # Render only the selected mode
#     if mode == "Maximize KPI (given budget)":
#         total_budget = st.number_input("Total Budget", min_value=0.0, value=10000.0, step=100.0, key="total_budget_max")
#         priority = st.selectbox("Optimization Priority", ["balanced", "impressions", "views", "engagement"], key="priority_max")
    
#         with st.expander("Advanced constraints (per-tier min/max)", expanded=False):
#             col1, col2 = st.columns(2)
#             min_alloc, max_alloc = {}, {}
#             with col1:
#                 st.subheader("Minimum Allocation")
#                 for t in TIERS:
#                     min_alloc[t] = st.number_input(f"Min {t}", min_value=0.0, value=0.0, step=100.0, key=f"min_{t}_max")
#             with col2:
#                 st.subheader("Maximum Allocation")
#                 for t in TIERS:
#                     max_alloc[t] = st.number_input(f"Max {t}", min_value=0.0, value=float(total_budget), step=100.0, key=f"max_{t}_max")
    
#         if st.button("Generate 5 scenarios", key="run_max"):
#             if any(min_alloc[t] > max_alloc[t] for t in TIERS):
#                 st.error("Infeasible: some Min > Max.")
#                 st.stop()
#             if sum(min_alloc[t] for t in TIERS) > total_budget:
#                 st.error("Infeasible: sum of minimums exceeds total budget.")
#                 st.stop()
    
#             scenarios = get_five_budget_scenarios(
#                 weights_df=weights_df,
#                 total_budget=float(total_budget),
#                 min_alloc={k: float(v) for k, v in min_alloc.items()},
#                 max_alloc={k: float(v) for k, v in max_alloc.items()},
#                 priority=priority,
#                 category=category
#             )
#             if not scenarios:
#                 st.error("No feasible scenarios.")
#             else:
#                 st.success("Generated scenarios.")
#                 scenario_ids = [f"Scenario {i+1}" for i in range(len(scenarios))]
#                 recs = []
#                 for i, s in enumerate(scenarios):
#                     for tier in DISPLAY_ORDER:
#                         recs.append({"Scenario": scenario_ids[i], "Tier": tier, "Allocation": float(s['allocation'].get(tier, 0.0))})
#                 chart_df = pd.DataFrame(recs)
#                 chart_df["TierOrder"] = chart_df["Tier"].map({t:i for i,t in enumerate(DISPLAY_ORDER)})
    
#                 chart = (
#                     alt.Chart(chart_df)
#                     .mark_bar()
#                     .encode(
#                         x=alt.X("Scenario:N", sort=scenario_ids),
#                         y=alt.Y("Allocation:Q", stack="zero", title="Allocation"),
#                         color=alt.Color("Tier:N", sort=DISPLAY_ORDER, scale=alt.Scale(domain=DISPLAY_ORDER)),
#                         order=alt.Order("TierOrder:Q"),
#                         tooltip=[alt.Tooltip("Scenario:N"), alt.Tooltip("Tier:N"), alt.Tooltip("Allocation:Q", format=",.2f")]
#                     ).properties(height=420)
#                 )
#                 st.altair_chart(chart, use_container_width=True)
    
#                 kpi_df = pd.DataFrame([{
#                     "Scenario": scenario_ids[i],
#                     "Impressions": s['impressions'],
#                     "Views": s['views'],
#                     "Engagement": s['engagement'],
#                     "Total KPI": s['total_kpi'],
#                 } for i, s in enumerate(scenarios)])
#                 st.dataframe(kpi_df.style.format({"Impressions":"{:,.2f}","Views":"{:,.2f}","Engagement":"{:,.2f}","Total KPI":"{:,.2f}"}), hide_index=True, use_container_width=True)
    
#     else:
#         # Min budget mode (no fixed-mix option; advanced constraints shown)
#         kpi_type = st.selectbox("KPI to target", ["impressions", "views", "engagement"], key="kpi_tgt")
#         target_value = st.number_input(f"Target {kpi_type.title()}", min_value=0.0, value=1_000_000.0, step=1000.0, key="target_value_tgt")
    
#         with st.expander("Advanced constraints (per-tier min/max)", expanded=True):
#             col1, col2 = st.columns(2)
#             min_alloc, max_alloc = {}, {}
#             with col1:
#                 st.subheader("Minimum Allocation")
#                 for t in TIERS:
#                     min_alloc[t] = st.number_input(f"Min {t}", min_value=0.0, value=0.0, step=100.0, key=f"min_{t}_tgt")
#             with col2:
#                 st.subheader("Maximum Allocation")
#                 for t in TIERS:
#                     max_alloc[t] = st.number_input(f"Max {t}", min_value=0.0, value=BIG_MAX, step=100.0, key=f"max_{t}_tgt")
    
#         if st.button("Generate 5 scenarios to achieve KPI", key="run_tgt_free"):
#             try:
#                 scenarios = get_five_target_scenarios(
#                     weights_df=weights_df,
#                     target_value=float(target_value),
#                     kpi_type=kpi_type,
#                     min_alloc=min_alloc, max_alloc=max_alloc,
#                     category=category  # uses internal 1.5% tolerance automatically
#                 )
#             except Exception as e:
#                 st.exception(e)
#                 st.stop()
    
#             if not scenarios:
#                 st.error("No feasible scenarios for the given target and constraints.")
#             else:
#                 st.success("Generated scenarios.")
#                 scenario_ids = [f"Scenario {i+1}" for i in range(len(scenarios))]
#                 recs = []
#                 for i, s in enumerate(scenarios):
#                     for tier in DISPLAY_ORDER:
#                         recs.append({"Scenario": scenario_ids[i], "Tier": tier, "Allocation": float(s['allocation'].get(tier, 0.0))})
#                 chart_df = pd.DataFrame(recs)
#                 chart_df["TierOrder"] = chart_df["Tier"].map({t:i for i,t in enumerate(DISPLAY_ORDER)})
    
#                 chart = (
#                     alt.Chart(chart_df)
#                     .mark_bar()
#                     .encode(
#                         x=alt.X("Scenario:N", sort=scenario_ids),
#                         y=alt.Y("Allocation:Q", stack="zero", title="Allocation (Budget)"),
#                         color=alt.Color("Tier:N", sort=DISPLAY_ORDER, scale=alt.Scale(domain=DISPLAY_ORDER)),
#                         order=alt.Order("TierOrder:Q"),
#                         tooltip=[alt.Tooltip("Scenario:N"), alt.Tooltip("Tier:N"), alt.Tooltip("Allocation:Q", format=",.2f")]
#                     ).properties(height=420)
#                 )
#                 st.altair_chart(chart, use_container_width=True)
    
#                 kpi_df = pd.DataFrame([{
#                     "Scenario": scenario_ids[i],
#                     "Required Budget": s['required_budget'],
#                     "Impressions": s['impressions'],
#                     "Views": s['views'],
#                     "Engagement": s['engagement'],
#                     "Total KPI": s['total_kpi'],
#                 } for i, s in enumerate(scenarios)])
#                 st.dataframe(kpi_df.style.format({
#                     "Required Budget":"{:,.2f}",
#                     "Impressions":"{:,.2f}",
#                     "Views":"{:,.2f}",
#                     "Engagement":"{:,.2f}",
#                     "Total KPI":"{:,.2f}",
#                 }), hide_index=True, use_container_width=True)
    
# #Page4
# if st.session_state.page == "GEN AI":
#     st.title(" COMMING SOON...")
#     # import pydata_google_auth
    
#     # SCOPES = [
#     #     'https://www.googleapis.com/auth/cloud-platform',
#     #     'https://www.googleapis.com/auth/drive',
#     # ]
    
#     # credentials = pydata_google_auth.get_user_credentials(
#     #     SCOPES,
#     #     auth_local_webserver=True,
#     # )
    
#     # query = """
#     # SELECT * FROM `pj-allclient-4d2mru.view.industry_norm_fbgg_category_stats_view`
#     # """
#     # df = pd.read_gbq(query=query, project_id = "pj-newnestle-vmtifr", credentials=credentials, dialect = 'standard')
    
#     # # Show the data in Streamlit
#     # st.dataframe(df)
# # # Page 4: GEN AI with PandasAI (Free Hugging Face Model, No API Key + Clear Chat)

# # if st.session_state.page == "GEN AI":
# #     import streamlit as st
# #     import pandas as pd
# #     from pandasai import SmartDataframe
# #     from transformers import pipeline
# #     from pandasai.llm.base import LLM

# #     # Local model wrapper
# #     class LocalHuggingFaceLLM(LLM):
# #         def __init__(self, model_name="google/flan-t5-base"):
# #             self.model_name = model_name
# #             self.generator = pipeline("text2text-generation", model=model_name)

# #         def call(self, prompt: str, *args, **kwargs) -> str:
# #             result = self.generator(prompt, max_length=256, do_sample=True)[0]["generated_text"]
# #             return result

# #         @property
# #         def type(self):
# #             return "local-huggingface"

# #     st.title("📊 GEN AI: Chat with Your Data (No API Key)")

# #     # Session state for chat
# #     if "chat_prompt" not in st.session_state:
# #         st.session_state.chat_prompt = ""
# #     if "chat_response" not in st.session_state:
# #         st.session_state.chat_response = ""

# #     uploaded_file = st.file_uploader("📎 Upload a CSV file", type=["csv"])
# #     if uploaded_file:
# #         df = pd.read_csv(uploaded_file)
# #         st.write("🧾 Data Preview:", df.head())

# #         llm = LocalHuggingFaceLLM()

# #         sdf = SmartDataframe(
# #             df,
# #             config={
# #                 "llm": llm,
# #                 "enable_cache": False,
# #                 "enable_memory": True,
# #                 "verbose": True,
# #             },
# #         )

# #         # Input + buttons
# #         col1, col2 = st.columns([3, 1])
# #         with col1:
# #             st.session_state.chat_prompt = st.text_input(
# #                 "💬 Ask a question about your data (e.g. 'Which category has the lowest CPM?')",
# #                 value=st.session_state.chat_prompt,
# #                 key="prompt_input"
# #             )

# #         with col2:
# #             if st.button("🧹 Clear Chat"):
# #                 st.session_state.chat_prompt = ""
# #                 st.session_state.chat_response = ""

# #         # Handle question
# #         if st.session_state.chat_prompt:
# #             with st.spinner("🤖 Thinking..."):
# #                 try:
# #                     st.session_state.chat_response = sdf.chat(st.session_state.chat_prompt)
# #                 except Exception as e:
# #                     st.session_state.chat_response = f"❌ Error: {e}"

# #         # Show response
# #         if st.session_state.chat_response:
# #             st.write("✅ Response:", st.session_state.chat_response)

# # ---------- Page 5: Embedded Looker Studio Dashboard ----------
# if st.session_state.page == "Dashboard":
#     st.title("📊 Live Dashboard")
#     st.markdown("Click below to view your dashboard in a new tab:")

#     # # Display an image or icon (optional)
#     # st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Google_Data_Studio_Logo.svg/512px-Google_Data_Studio_Logo.svg.png", width=100)

#     # Add a button to open the Looker Studio link
#     dashboard_url = "https://lookerstudio.google.com/reporting/2612a10a-44a2-4b2d-866d-58b4cd13023e/page/bIqhE"
#     st.markdown(f"""
#         <a href="{dashboard_url}" target="_blank">
#             <button style="background-color:#4285F4;color:white;padding:10px 20px;border:none;border-radius:8px;font-size:16px;">
#                 🔗 Open Dashboard
#             </button>
#         </a>
#     """, unsafe_allow_html=True)
