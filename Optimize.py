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
from textwrap import dedent
import urllib.parse as _url

# ===================== FRONTGATE v2 (fixed logo + intro icon size + nav shine) =====================
# วางบล็อกนี้ไว้เหนือโค้ดแอปเดิมทั้งหมด

# --- FrontGate state ---
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("fg_intro_done", False)
st.session_state.setdefault("fg_handoff_once", False)

# --- Credentials ---
_FG_VALID_USERS = {"mbcs":"1234","mbcs1":"5678","admin":"adminpass"}

# --- Assets / options ---
_FG_LOGO_URL = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
_FG_SHOW_TICKER = True
_FG_TICKER_ITEMS = [
    {"text": "MBCS AI Optimization Tool", "color": "#000000"},
    {"text": "Smart budget simulation",   "color": "#16a34a"},
    {"text": "Influencer optimization",   "color": "#2563eb"},
]
_FG_TAGLINE = "Secure access • Smart budget simulation • Influencer optimization"

# --- SCOPED CSS (ไม่ไปทับสไตล์ในแอปเดิม) + NAV SHINE สำหรับ .nav-scope ---
st.markdown("""
<style>
/* ---------- FrontGate scope ---------- */
.fg-scope .fg-wrap { position:relative; padding-top:4px; }
.fg-scope .fg-ambient { position:absolute; inset:-40px -10px -10px -10px; z-index:0; pointer-events:none; }
.fg-scope .fg-ambient::before,.fg-scope .fg-ambient::after,.fg-scope .fg-ambient i{
  content:""; position:absolute; left:50%; transform:translateX(-50%); border-radius:50%; filter:blur(20px);
}
.fg-scope .fg-ambient::before{ top:-30px; width:520px; height:520px; background: radial-gradient(closest-side, rgba(59,130,246,.40), rgba(59,130,246,0) 70%); opacity:.38; animation: fg_g1 7s ease-in-out infinite; }
.fg-scope .fg-ambient::after{ top:40px; width:720px; height:720px; background: radial-gradient(closest-side, rgba(167,139,250,.33), rgba(167,139,250,0) 72%); opacity:.28; animation: fg_g2 10s ease-in-out infinite .8s; }
.fg-scope .fg-ambient i{ top:220px; width:420px; height:420px; background: radial-gradient(closest-side, rgba(16,185,129,.28), rgba(16,185,129,0) 70%); opacity:.22; animation: fg_g3 12s ease-in-out infinite .4s; }
@keyframes fg_g1{0%,100%{opacity:.22; transform:translateX(-50%) scale(.96)}50%{opacity:.55; transform:translateX(-50%) scale(1.06)}}
@keyframes fg_g2{0%,100%{opacity:.18; transform:translateX(-50%) scale(.98)}50%{opacity:.40; transform:translateX(-50%) scale(1.05)}}
@keyframes fg_g3{0%,100%{opacity:.14; transform:translateX(-50%) scale(.97)}50%{opacity:.32; transform:translateX(-50%) scale(1.04)}}

.fg-scope .fg-title{
  font-weight:800; line-height:1.1; margin:.1rem 0 .6rem 0; text-align:center; font-size:40px;
  background: linear-gradient(90deg, #10b981, #22d3ee, #3b82f6, #10b981);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  background-size:200% auto; animation: fg_grad 10s linear infinite;
  text-shadow:0 1px 0 rgba(255,255,255,.4); position:relative; z-index:1;
}
@keyframes fg_grad{0%{background-position:0% 50%}100%{background-position:200% 50%}}
.fg-scope .fg-sub{ color:#526273; text-align:center; margin-bottom:18px; position:relative; z-index:1; }

/* โลโก้กลม + วงแหวน + วิบวับ (บังคับกลมด้วย overflow+object-fit) */
.fg-scope .fg-logo{
  position:relative; width:130px; height:130px; margin:0 auto 10px auto; z-index:1;
  border-radius:50%; overflow:hidden;
}
.fg-scope .fg-logo::before{
  content:""; position:absolute; inset:-10px; border-radius:50%;
  background: conic-gradient(from 0deg, #22d3ee, #a78bfa, #22c55e, #22d3ee);
  animation: fg_spin 10s linear infinite; filter: blur(10px); opacity:.7;
}
.fg-scope .fg-logo img{
  position:relative; z-index:1; width:100%; height:100%;
  border-radius:50% !important; object-fit:cover; display:block;
  box-shadow: 0 8px 24px rgba(2,6,23,.25); animation: fg_pulse 4.5s ease-in-out infinite;
}
@keyframes fg_spin{to{transform:rotate(360deg)}}
@keyframes fg_pulse{0%,100%{box-shadow:0 8px 24px rgba(2,6,23,.25)}50%{box-shadow:0 8px 24px rgba(2,6,23,.25),0 0 28px rgba(167,139,250,.35)}}

.fg-scope .fg-card{ position:relative; z-index:1; border-radius:14px; border:1px solid #dbe7fb; background:#ffffffcc;
  box-shadow:0 10px 28px rgba(25,60,120,.14); padding:18px; overflow:hidden; }
.fg-scope .fg-card::after{ content:""; position:absolute; top:0; bottom:0; width:80px; left:-120px; z-index:0;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,.6), transparent);
  transform: skewX(-18deg); animation: fg_sweep 6s linear infinite; }
@keyframes fg_sweep{0%{left:-120px}100%{left:120%}}

.fg-scope .fg-pill{ width:min(720px,90vw); margin:0 auto 12px auto; border-radius:9999px; position:relative; overflow:hidden;
  background:linear-gradient(180deg,#fff,#f5f9ff); border:1px solid #e6eefb; box-shadow:0 10px 24px rgba(15,40,80,.12);}
.fg-scope .fg-sheen{ position:absolute; inset:0; pointer-events:none; width:80px;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,.55), transparent);
  transform: translateX(-150%) skewX(-18deg); animation: fg_sheen 8s linear infinite;}
@keyframes fg_sheen{0%{transform:translateX(-150%) skewX(-18deg)}100%{transform:translateX(250%) skewX(-18deg)}}
.fg-scope .fg-glass{ height:22px; background: linear-gradient(180deg, rgba(255,255,255,.95), rgba(255,255,255,.7));
  border:1px solid #e6eefb; border-radius:9999px; backdrop-filter: blur(6px); box-shadow:0 10px 24px rgba(15,40,80,.12); }

/* Intro content */
.fg-scope .fg-intro{ position:relative; border:1px solid #e6eefb; border-radius:16px; background:rgba(255,255,255,.86);
  box-shadow:0 14px 30px rgba(21,63,124,.12); padding:20px 22px; overflow:hidden; }
.fg-scope .fg-intro .fg-spark{
  content:""; position:absolute; inset:-10px; pointer-events:none;
  background:
    radial-gradient(6px 6px at 12% 18%, rgba(255,255,255,.9), rgba(255,255,255,0) 70%),
    radial-gradient(6px 6px at 80% 10%, rgba(255,255,255,.9), rgba(255,255,255,0) 70%),
    radial-gradient(8px 8px at 90% 62%, rgba(255,255,255,.9), rgba(255,255,255,0) 70%),
    radial-gradient(5px 5px at 6% 70%, rgba(255,255,255,.9), rgba(255,255,255,0) 70%);
  opacity:.45; animation: fg_twinkle 6s ease-in-out infinite;
}
@keyframes fg_twinkle{0%,100%{opacity:.18}50%{opacity:.6}}
.fg-scope .fg-feature{ display:flex; align-items:flex-start; gap:14px; margin: 14px 0 18px 0; }
.fg-scope .fg-feature .fg-txt{ color:#2b3f4d; line-height:1.5; font-size:16px; }
/* ขนาดไอคอน bullet ให้เล็กลงแน่นอน */
.fg-scope .fg-feature .fg-ico{ width:36px; height:36px; flex:0 0 36px; filter: drop-shadow(0 6px 10px rgba(34,197,94,.20)); }

/* SCOPED inputs/buttons ของ FrontGate เท่านั้น */
.fg-scope .stTextInput > div > div > input,
.fg-scope .stPassword > div > div > input { background:#f8fbff; border-radius:10px; }
.fg-scope .stButton > button{
  width:100%; border-radius:10px; height:44px; position:relative; z-index:1;
  background:linear-gradient(90deg, #22c55e, #06b6d4); border:none; color:white; font-weight:700; letter-spacing:.2px;
  box-shadow:0 8px 22px rgba(3,105,161,.28);
}
.fg-scope .stButton > button:hover{ filter:brightness(1.04); transform:translateY(-1px); }

/* ---------- NAV SHINE ADD-ON สำหรับแอปเดิม (เฉพาะ .nav-scope) ---------- */
.nav-scope { max-width: 900px; margin: 8px auto 6px auto; }
.nav-scope .nav-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }

.nav-scope .p1 div.stButton > button,
.nav-scope .p2 div.stButton > button,
.nav-scope .p3 div.stButton > button{
  position: relative; overflow: hidden; border-radius: 9999px;
  font-weight: 800; letter-spacing: .2px; font-size: 14px;
  border: 1px solid rgba(17,24,39,.08) !important;
  box-shadow: 0 10px 22px rgba(2,132,199,.18), inset 0 0 12px rgba(255,255,255,.12) !important;
  transition: transform .15s ease, filter .2s ease;
}

/* เปิดสี gradient ตอนปุ่มกดได้ */
.nav-scope .p1 div.stButton > button:not(:disabled){ background: linear-gradient(135deg, #22c55e, #06b6d4) !important; color:#fff !important; }
.nav-scope .p2 div.stButton > button:not(:disabled){ background: linear-gradient(135deg, #f59e0b, #ef4444) !important; color:#fff !important; }
.nav-scope .p3 div.stButton > button:not(:disabled){ background: linear-gradient(135deg, #6366f1, #22d3ee) !important; color:#fff !important; }

/* วิบวับ */
.nav-scope div.stButton > button::after{
  content:""; position:absolute; inset:0; pointer-events:none;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,.6), transparent);
  transform: translateX(-150%) skewX(-18deg); animation: navSheen 6s linear infinite;
}
@keyframes navSheen{ 0%{ transform: translateX(-150%) skewX(-18deg) } 100%{ transform: translateX(250%)  skewX(-18deg) } }
.nav-scope div.stButton > button:not(:disabled):hover{ transform: translateY(-2px) scale(1.01); filter: brightness(1.05); }

/* ปุ่มของหน้าปัจจุบัน (disabled) — สไตล์ KOL tag สีเขียว */
.nav-scope div.stButton > button:disabled{
  background: linear-gradient(180deg, #ecfdf5, #eafff7) !important;
  color:#0b1f16 !important;
  border: 2px solid #22c55e !important;
  box-shadow: 0 6px 16px rgba(16,185,129,.18) !important;
}
.nav-scope div.stButton > button:disabled::before{
  content:""; position:absolute; inset:0; border-radius:inherit;
  box-shadow: 0 0 0 2px rgba(34,197,94,.12) inset;
}
</style>
""", unsafe_allow_html=True)

# --- Ticker สำหรับหน้า FrontGate เท่านั้น ---
def _fg_banner():
    import json as _json
    items = _json.dumps(_FG_TICKER_ITEMS)
    if not _FG_SHOW_TICKER:
        return
    html = f"""
    <div class="fg-pill"><div class="fg-sheen"></div>
      <div id="fg-ticker" style="white-space:nowrap; position:relative; height:32px;">
        <div id="fg-track" style="display:flex; width:max-content; padding:6px 14px; gap:12px; animation:fg_marq 22s linear infinite; position:relative;"></div>
      </div>
    </div>
    <div class="fg-glass"></div>
    <style>
      @keyframes fg_marq {{ 0%{{ transform:translateX(0) }} 100%{{ transform:translateX(-50%) }} }}
      .fg-item {{ display:inline-flex; align-items:center; font-weight:600; }}
      .fg-sep {{ color:#94a3b8; margin:0 12px; }}
      #fg-track::after {{
        content:""; position:absolute; top:0; bottom:0; width:60px; left:-120px; pointer-events:none;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,.45), transparent);
        transform: skewX(-18deg); animation: fg_sweepT 7s linear infinite;
      }}
      @keyframes fg_sweepT {{ 0%{{ left:-120px }} 100%{{ left:120% }} }}
    </style>
    <script>
      const FG_ITEMS = {items};
      const FG_SEP = "•";
      const END_SPACE_PX = 40;
      const track = document.getElementById("fg-track");
      if (track && FG_ITEMS.length){{
        const make = () => {{
          const frag = document.createDocumentFragment();
          FG_ITEMS.forEach((it,i) => {{
            const s = document.createElement("span"); s.className="fg-item"; s.style.color=it.color; s.textContent=it.text; frag.appendChild(s);
            if (i<FG_ITEMS.length-1){{ const sep=document.createElement("span"); sep.className="fg-sep"; sep.textContent=FG_SEP; frag.appendChild(sep); }}
          }});
          const spacer=document.createElement("span"); spacer.style.display="inline-block"; spacer.style.width=END_SPACE_PX+"px"; frag.appendChild(spacer);
          return frag;
        }};
        const c1=document.createElement("div"); c1.appendChild(make());
        const c2=document.createElement("div"); c2.setAttribute("aria-hidden","true"); c2.appendChild(make());
        track.appendChild(c1); track.appendChild(c2);
        requestAnimationFrame(()=>{{ const w=c1.getBoundingClientRect().width; const dur=Math.max(16, w/90); track.style.animationDuration = dur + "s"; }});
      }}
    </script>
    """
    st.components.v1.html(html, height=110, scrolling=False)

# --- Login ---
def _fg_login():
    st.markdown('<div class="fg-scope"><div class="fg-wrap"><div class="fg-ambient"></div><i class="fg-ambient"></i>', unsafe_allow_html=True)
    _fg_banner()
    col = st.columns([1,1,1])[1]
    with col:
        # บังคับให้เป็นวงกลมแน่นอนด้วย style ตรง
        st.markdown(f'<div class="fg-logo"><img src="{_FG_LOGO_URL}" alt="logo" /></div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;justify-content:center;font-size:28px;margin-bottom:4px;">🔒</div>', unsafe_allow_html=True)
    st.markdown('<div class="fg-title">WELCOME TO NEST<br/>OPTIMIZED TOOL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fg-sub">{_FG_TAGLINE}</div>', unsafe_allow_html=True)

    st.markdown('<div class="fg-card">', unsafe_allow_html=True)
    with st.form("fg_login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        ok = st.form_submit_button("Sign in")
    st.markdown('</div></div></div>', unsafe_allow_html=True)

    if ok:
        if u in _FG_VALID_USERS and p == _FG_VALID_USERS[u]:
            st.session_state.authenticated = True
            st.session_state.fg_intro_done = False
            st.success("Signed in successfully.")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# --- Introduction ---
def _fg_intro():
    st.markdown('<div class="fg-scope"><div class="fg-wrap"><div class="fg-ambient"></div><i class="fg-ambient"></i>', unsafe_allow_html=True)
    _fg_banner()
    col = st.columns([1,1,1])[1]
    with col:
        st.markdown(f'<div class="fg-logo"><img src="{_FG_LOGO_URL}" alt="logo" /></div>', unsafe_allow_html=True)

    st.markdown('<div class="fg-title" style="font-size:36px;margin-bottom:6px;">Introducing NEST OPTIMIZER</div>', unsafe_allow_html=True)
    st.markdown("""
      <div class="fg-intro">
        <div class="fg-spark"></div>
        <p style="color:#344b5c;line-height:1.55;font-size:16px;margin:0 0 16px 0;">
          In a world with countless influencers across countless platforms, knowing where to begin is the biggest challenge.
          "NEST OPTIMIZER" is our proprietary KOL engine, designed to bring precision to influencer marketing and solve the two biggest challenges in the industry:
        </p>

        <div class="fg-feature">
          <!-- icon 36x36 แน่นอน -->
          <svg class="fg-ico" width="36" height="36" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <polygon points="32,8 52,44 12,44" fill="#16a34a" opacity=".85"/>
            <rect x="10" y="48" width="44" height="6" rx="3" fill="#10b981" opacity=".8"/>
          </svg>
          <div class="fg-txt">
            <span style="display:inline-block;padding:6px 12px;border-radius:10px;background:#ecfdf5;border:2px solid #22c55e;color:#0b1f16;font-weight:900;letter-spacing:.3px;text-transform:uppercase;position:relative;overflow:hidden;box-shadow:0 0 0 2px rgba(34,197,94,.10) inset, 0 6px 16px rgba(16,185,129,.18);">KOL TIER OPTIMIZATION</span>
            Strategically allocates your budget across influencer tiers to ensure maximum impact and cost efficiency.
          </div>
        </div>

        <div class="fg-feature">
          <svg class="fg-ico" width="36" height="36" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="16" cy="20" r="6" fill="#22c55e"/>
            <circle cx="48" cy="20" r="6" fill="#22c55e"/>
            <circle cx="32" cy="46" r="7" fill="#16a34a"/>
            <line x1="20" y1="24" x2="28" y2="40" stroke="#16a34a" stroke-width="3" />
            <line x1="44" y1="24" x2="36" y2="40" stroke="#16a34a" stroke-width="3" />
          </svg>
          <div class="fg-txt">
            <span style="display:inline-block;padding:6px 12px;border-radius:10px;background:#ecfdf5;border:2px solid #22c55e;color:#0b1f16;font-weight:900;letter-spacing:.3px;text-transform:uppercase;position:relative;overflow:hidden;box-shadow:0 0 0 2px rgba(34,197,94,.10) inset, 0 6px 16px rgba(16,185,129,.18);">KOL LIST OPTIMIZATION</span>
            Selects the most effective creators within each tier, based on their performance and relevance.
          </div>
        </div>

        <p style="color:#344b5c;line-height:1.55;font-size:16px;margin:0;">
          This is where we bring science to the art of influencer marketing. Our platform allows us to combine human
          expertise with data-driven insights. It provides a scientifically-backed KOL strategy that ensures every dollar
          spent delivers maximum effectiveness and cost efficiency, giving us a unique competitive advantage in the market.
        </p>
      </div>
    """, unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button("Next ▶", use_container_width=True, key="fg_next"):
            st.session_state.fg_intro_done = True
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

# --- Router (เหมือน v2 เดิม) ---
def frontgate():
    if not st.session_state.get("authenticated", False):
        _fg_login()
        st.stop()

    if not st.session_state.get("fg_intro_done", False):
        _fg_intro()
        st.stop()

    # ให้ตัววิ่งของแอปเดิมแสดงเสมอ
    st.session_state.ticker_rendered_once = False

    # ครั้งแรกเข้าสู่แอปเดิม -> บังคับหน้า Simulation Budget
    if not st.session_state.get("fg_handoff_once", False):
        try:
            st.session_state.page = "Simulation Budget"
            try:
                st.query_params.clear()
            except Exception:
                st.experimental_set_query_params()
        finally:
            st.session_state.fg_handoff_once = True
    return

frontgate()
# ===================== END FRONTGATE =====================


# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="MBCS Optimize Tool", page_icon="🔒", layout="wide")

# -------------------- SESSION STATE --------------------
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("page", "Simulation Budget")
st.session_state.setdefault("prev_page", None)
st.session_state.setdefault("ticker_rendered_once", False)  # กันซ้ำจากฝั่งเราเอง

# Shared data (ถ้ามีการใช้ต่อ)
if "inputs" not in st.session_state:
    st.session_state.inputs = {"VIP": 0, "Mega": 0, "Macro": 0, "Mid": 0, "Micro": 0, "Nano": 0}

# -------------------- OPTIONS --------------------
logo_url = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
SHOW_TICKER_APP = True  # แสดงตัววิ่งหลังล็อกอิน
TICKER_ITEMS = [
    {"text": "MBCS AI Optimization Tool", "color": "#000000"},
    {"text": "Smart budget simulation",   "color": "#16a34a"},
    {"text": "Influencer optimization",   "color": "#2563eb"},
]

# -------------------- GLOBAL STYLES --------------------
st.markdown("""
<style>
.appview-container .main, .block-container { max-width: 1100px !important; margin: auto; }

/* พื้นหลัง */
body {
  background:
    radial-gradient(1200px 600px at 50% -10%, rgba(59,130,246,.15), transparent 60%),
    radial-gradient(900px 500px at -20% 20%, rgba(16,185,129,.12), transparent 60%),
    linear-gradient(180deg, #f7fbff 0%, #eef5ff 60%, #eaf2ff 100%) !important;
}

/* Ticker pills (ของเรา) */
.top-wrap { margin-top: 10px; margin-bottom: 22px; }
.pill { width: min(720px, 90vw); margin: 0 auto 12px auto; border-radius: 9999px; position:relative; overflow:hidden;
  background: linear-gradient(180deg, #ffffff, #f5f9ff); border:1px solid #e6eefb; box-shadow:0 10px 24px rgba(15,40,80,.12); }
.pill .sheen{ content:""; position:absolute; inset:0; background: linear-gradient(120deg, transparent, rgba(255,255,255,.55), transparent); width:80px; transform: translateX(-150%) skewX(-18deg); animation: sheenMove 8s linear infinite; pointer-events:none; }
@keyframes sheenMove { 0%{ transform: translateX(-150%) skewX(-18deg)} 100%{ transform: translateX(250%) skewX(-18deg)} }
.glass{ height:22px; background: linear-gradient(180deg, rgba(255,255,255,.95), rgba(255,255,255,.7)); border:1px solid #e6eefb; border-radius:9999px; backdrop-filter: blur(6px); box-shadow:0 10px 24px rgba(15,40,80,.12); }

/* Header หลังล็อกอิน */
.app-header{
  position: relative; overflow: hidden; padding: 26px 26px 20px; border-radius: 18px;
  background: rgba(255,255,255,.78); backdrop-filter: blur(8px);
  border: 1px solid rgba(17,24,39,.08); box-shadow: 0 12px 35px rgba(17,24,39,.10); margin-bottom: 18px;
}
.app-header:before{ content:""; position:absolute; inset:-2px;
  background: conic-gradient(from 0deg, #6366f1, #22d3ee, #a78bfa, #6366f1);
  filter: blur(28px); opacity:.25; animation: spin 10s linear infinite; }
.shine{ position:absolute; inset:1px; border-radius:16px;
  background: linear-gradient(120deg, rgba(255,255,255,.18), transparent 35%, transparent 65%, rgba(255,255,255,.18));
  background-size:220% 100%; animation: gradientMove 6s linear infinite; pointer-events:none; }
.headline{ font-size: clamp(26px, 4.2vw, 42px); font-weight: 900; letter-spacing:.4px; background: linear-gradient(90deg, #0f172a, #1e293b, #0f172a); -webkit-background-clip: text; background-clip: text; color: transparent; }
.subline{ margin-top: 6px; color:#4b5563; opacity:.95; font-size: clamp(12px, 1.6vw, 14px); }

/* Brand hero */
.brand-hero{ position:relative; margin: 4px auto 8px auto; display:flex; justify-content:center; }
.brand-hero .brand-stage{ position:relative; z-index:1; }
.brand-ambient{ position:absolute; inset:-40px 0 -10px 0; z-index:0; pointer-events:none; }
.brand-ambient .g1, .brand-ambient .g2, .brand-ambient .g3{
  position:absolute; left:50%; transform:translateX(-50%); border-radius:50%; filter: blur(20px);
}
.brand-ambient .g1{ top:-30px; width:520px; height:520px; background: radial-gradient(closest-side, rgba(59,130,246,.40), rgba(59,130,246,0) 70%); opacity:.38; animation: bh_glow1 7s ease-in-out infinite; }
.brand-ambient .g2{ top:40px; width:720px; height:720px; background: radial-gradient(closest-side, rgba(167,139,250,.33), rgba(167,139,250,0) 72%); opacity:.28; animation: bh_glow2 10s ease-in-out infinite .8s; }
.brand-ambient .g3{ top:220px; width:420px; height:420px; background: radial-gradient(closest-side, rgba(16,185,129,.28), rgba(16,185,129,0) 70%); opacity:.22; animation: bh_glow3 12s ease-in-out infinite .4s; }
@keyframes bh_glow1{ 0%,100%{opacity:.22; transform:translateX(-50%) scale(.96)} 50%{opacity:.55; transform:translateX(-50%) scale(1.06)} }
@keyframes bh_glow2{ 0%,100%{opacity:.18; transform:translateX(-50%) scale(.98)} 50%{opacity:.40; transform:translateX(-50%) scale(1.05)} }
@keyframes bh_glow3{ 0%,100%{opacity:.14; transform:translateX(-50%) scale(.97)} 50%{opacity:.32; transform:translateX(-50%) scale(1.04)} }
.brand-logo{ position:relative; width:120px; height:120px; }
.brand-logo::before{
  content:""; position:absolute; inset:-10px; border-radius:50%;
  background: conic-gradient(from 0deg, #22d3ee, #a78bfa, #22c55e, #22d3ee);
  animation: bh_spin 10s linear infinite; filter: blur(10px); opacity:.7;
}
.brand-logo img{
  position:relative; z-index:1; width:100%; height:100%; border-radius:50%;
  box-shadow: 0 8px 24px rgba(2,6,23,.25); animation: bh_pulse 4.5s ease-in-out infinite;
}

/* Current page pill */
.page-pill{
  display: inline-flex; align-items: center; gap:10px; padding: 10px 16px; margin-top: 10px;
  border-radius: 999px; background: linear-gradient(135deg, rgba(99,102,241,.08), rgba(34,211,238,.06)), #ffffff;
  border: 1px solid rgba(17,24,39,.10); color:#111827; font-weight: 700;
  box-shadow: 0 4px 16px rgba(17,24,39,.08); position: relative; overflow: hidden;
}
.page-pill .dot{ width: 10px; height: 10px; border-radius: 50%; background: #6366f1; box-shadow: 0 0 10px rgba(99,102,241,.6); }
.page-pill .glowline{ position:absolute; inset:1px; border-radius:999px; background: linear-gradient(120deg, rgba(255,255,255,.6), transparent 40%, transparent 60%, rgba(255,255,255,.6)); background-size: 200% 100%; animation: gradientMove 3.2s linear infinite; pointer-events:none; }

@keyframes gradientMove { 0%{background-position:0% 50%} 100%{background-position:200% 50%} }
@keyframes spin{ to{ transform: rotate(360deg);} }
</style>
""", unsafe_allow_html=True)

# -------------------- Inject JS: ลบตัววิ่งซ้ำ (ข้าม iframe) + ซ่อนแบนเนอร์สีเขียว --------------------
def inject_cleanup_js():
    st.markdown("""
    <script>
    (function(){
      function hideDuplicateTickers(){
        const iframes = Array.from(document.querySelectorAll('iframe'));
        const tickers = [];
        for (const f of iframes){
          try{
            const doc = f.contentDocument || f.contentWindow?.document;
            if(!doc) continue;
            const txt = (doc.body?.innerText || "").replace(/\\s+/g,' ').trim();
            // ตรวจจับจากข้อความ 3 ชิ้นใน ticker
            if (txt.includes('MBCS AI Optimization Tool') &&
                txt.includes('Smart budget simulation') &&
                txt.includes('Influencer optimization')){
              tickers.push(f);
            }
          }catch(e){/* sandbox บางกรณี */}
        }
        if (tickers.length > 1){
          // เก็บตัวสุดท้าย (ด้านล่าง) ไว้ตัวเดียว
          for(let i=0;i<tickers.length-1;i++){
            tickers[i].style.display = 'none';
          }
        }
      }

      function hideLoggedInBanner(){
        const alerts = Array.from(document.querySelectorAll('[role="alert"]'));
        alerts.forEach(a=>{
          const t = (a.innerText||"").trim();
          if (t.startsWith('You are logged in. Build your app content here.')){
            a.style.display = 'none';
          }
        });
      }

      // เรียกซ้ำหลายครั้งเผื่อ DOM อัปเดต
      hideDuplicateTickers(); hideLoggedInBanner();
      setTimeout(hideDuplicateTickers, 250);  setTimeout(hideLoggedInBanner, 250);
      setTimeout(hideDuplicateTickers, 800);  setTimeout(hideLoggedInBanner, 800);
      setTimeout(hideDuplicateTickers, 2000); setTimeout(hideLoggedInBanner, 2000);
    })();
    </script>
    """, unsafe_allow_html=True)

# -------------------- TICKER (render once from our side) --------------------
def render_top_banner_once():
    if st.session_state.ticker_rendered_once or not SHOW_TICKER_APP:
        return
    import json as _json
    items_json = _json.dumps(TICKER_ITEMS)
    html = f"""
    <div class="top-wrap">
      <div class="pill">
        <div class="sheen"></div>
        <div id="ticker" style="white-space:nowrap; position:relative; height:32px;">
          <div id="track" style="display:flex; width:max-content; padding:6px 14px; gap:12px; animation:marq 22s linear infinite; position:relative;"></div>
        </div>
      </div>
      <div class="glass pill"></div>
    </div>
    <style>
      @keyframes marq {{ 0%{{ transform:translateX(0) }} 100%{{ transform:translateX(-50%) }} }}
      .t-item {{ display:inline-flex; align-items:center; font-weight:600; }}
      .t-sep {{ color:#94a3b8; margin:0 12px; }}
      #track::after {{
        content:""; position:absolute; top:0; bottom:0; width:60px; left:-120px; pointer-events:none;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,.45), transparent);
        transform: skewX(-18deg); animation: sweepT 7s linear infinite;
      }}
      @keyframes sweepT {{ 0%{{ left:-120px }} 100%{{ left:120% }} }}
    </style>
    <script>
      const ITEMS = {items_json};
      const SEPARATOR = "•";
      const END_SPACE_PX = 40;
      const track = document.getElementById("track");
      if (track && ITEMS.length){{
        const make = () => {{
          const frag = document.createDocumentFragment();
          ITEMS.forEach((it, i) => {{
            const s = document.createElement("span"); s.className = "t-item"; s.style.color = it.color; s.textContent = it.text; frag.appendChild(s);
            if (i < ITEMS.length - 1) {{ const sep = document.createElement("span"); sep.className = "t-sep"; sep.textContent = SEPARATOR; frag.appendChild(sep); }}
          }});
          const spacer = document.createElement("span"); spacer.style.display = "inline-block"; spacer.style.width = END_SPACE_PX + "px"; frag.appendChild(spacer);
          return frag;
        }};
        const c1 = document.createElement("div"); c1.appendChild(make());
        const c2 = document.createElement("div"); c2.setAttribute("aria-hidden","true"); c2.appendChild(make());
        track.appendChild(c1); track.appendChild(c2);
        requestAnimationFrame(() => {{
          const w = c1.getBoundingClientRect().width; const dur = Math.max(16, w / 90);
          track.style.animationDuration = dur + "s";
        }});
      }}
    </script>
    """
    st.components.v1.html(html, height=110, scrolling=False)
    st.session_state.ticker_rendered_once = True  # กันซ้ำจากฝั่งเราเอง

# -------------------- HEADER / BRAND HERO --------------------
def render_header():
    st.markdown("""
    <div class="app-header">
      <div class="shine"></div>
      <div class="headline">📁 Welcome To MBCS Optimize Tool</div>
      <div class="subline">Smart budget simulation • Influencer performance • Optimization</div>
    </div>
    """, unsafe_allow_html=True)

def render_brand_hero():
    st.markdown(f"""
    <div class="brand-hero">
      <div class="brand-ambient">
        <span class="g1"></span><span class="g2"></span><span class="g3"></span>
      </div>
      <div class="brand-stage">
        <div class="brand-logo"><img src="{logo_url}" alt="logo"/></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- NAV (ellipse pills, no rerun warning) --------------------
def sync_page_from_query():
    try:
        qp = st.query_params
        if "page" in qp:
            st.session_state.page = qp["page"]
    except Exception:
        qp = st.experimental_get_query_params()
        if "page" in qp:
            st.session_state.page = qp["page"][0]

def set_page(name: str):
    st.session_state.page = name
    try:
        st.query_params.update({"page": name})
    except Exception:
        st.experimental_set_query_params(page=name)

def render_nav_pills():
    st.markdown("""
    <style>
    .nav-scope { max-width: 900px; margin: 8px auto 6px auto; }
    .nav-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
    .nav-scope div.stButton > button{
      height: 46px; border-radius: 9999px; width: 100%;
      font-weight: 800; letter-spacing: .2px; font-size: 14px; color: #fff;
      border: 1px solid rgba(17,24,39,.08);
      box-shadow: 0 10px 22px rgba(2,132,199,.18), inset 0 0 12px rgba(255,255,255,.12);
      transition: transform .15s ease, box-shadow .2s ease, filter .2s ease;
    }
    .nav-scope div.stButton > button:hover{ transform: translateY(-2px) scale(1.01); filter: brightness(1.04); }
    .nav-scope div.stButton > button:active{ transform: translateY(0) scale(.98); }
    .nav-scope .p1 div.stButton > button{ background: linear-gradient(135deg, #22c55e, #06b6d4); }
    .nav-scope .p2 div.stButton > button{ background: linear-gradient(135deg, #f97316, #ef4444); }
    .nav-scope .p3 div.stButton > button{ background: linear-gradient(135deg, #6366f1, #22d3ee); }
    .nav-scope div.stButton > button:disabled{
      cursor: default; filter: none; transform: none;
      outline: 3px solid rgba(99,102,241,.20);
      box-shadow: 0 16px 30px rgba(2,132,199,.25);
    }
    </style>
    """, unsafe_allow_html=True)

    sync_page_from_query()
    curr = st.session_state.page

    st.markdown('<div class="nav-scope"><div class="nav-grid">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="p1">', unsafe_allow_html=True)
        st.button("📂 Simulation Budget", use_container_width=True,
                  disabled=(curr == "Simulation Budget"), on_click=set_page, args=("Simulation Budget",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="p2">', unsafe_allow_html=True)
        st.button("📊 Influencer Performance", use_container_width=True,
                  disabled=(curr == "Influencer Performance"), on_click=set_page, args=("Influencer Performance",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="p3">', unsafe_allow_html=True)
        st.button("🧾 Optimized Budget", use_container_width=True,
                  disabled=(curr == "Optimized Budget"), on_click=set_page, args=("Optimized Budget",))
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------- PAGE CONTENT DUMMIES --------------------
def page_simulation_budget(): return
def page_influencer_performance(): return
def page_optimized_budget(): return

# ==================== MAIN (หลังล็อกอินเท่านั้น) ====================
if not st.session_state.authenticated:
    # คงหน้า Login ของคุณไว้ตามเดิม (เราไม่แตะ)
    st.info("Please sign in on your existing login view.")
    st.stop()

# 1) เคลียร์ตัววิ่งซ้ำ + ซ่อนแบนเนอร์เขียว (ทำก่อนเรนเดอร์อย่างอื่น)
inject_cleanup_js()

# 2) เรนเดอร์ตัววิ่งของเราเอง “แค่ครั้งเดียว” ต่อรอบ
render_top_banner_once()

# 3) โลโก้ + Header + Nav
render_brand_hero()
render_header()
render_nav_pills()

# 4) Current page pill
st.markdown(f"""
<div class="page-pill">
  <span class="dot"></span>
  <span>Current Page: <strong>{st.session_state.page}</strong></span>
  <div class="glowline"></div>
</div>
""", unsafe_allow_html=True)

# 5) สลับเพจ (ปล่อยว่างเพื่อไม่ทับคอนเทนต์จริงของคุณ)
if st.session_state.page == "Simulation Budget":
    page_simulation_budget()
elif st.session_state.page == "Influencer Performance":
    page_influencer_performance()
else:
    page_optimized_budget()


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

    # ===================== TITLE =====================
    st.title("📊 Simulation Budget")
    
    # ===================== LOAD weights_df =====================
    # Expect weights_df to be prepared elsewhere. We support both globals() and st.session_state.
    if "weights_df" in st.session_state:
        weights_df = st.session_state["weights_df"]
    elif "weights_df" in globals():
        weights_df = globals()["weights_df"]
    else:
        st.error("weights_df is not defined. Please load it before this page. Required columns: Category, Tier, Platform, KPI, Weights")
        st.stop()
    
    # Only these KPIs are taken from the sheet. CPE/CPShare are derived after simulate.
    ALLOWED_KPIS = {"Impression", "View", "Engagement", "Share"}
    TIERS = ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']
    
    required_cols = {'Category', 'Tier', 'Platform', 'KPI', 'Weights'}
    missing_cols = required_cols - set(weights_df.columns)
    if missing_cols:
        st.error(f"weights_df missing columns: {missing_cols}")
        st.stop()
    
    weights_df = weights_df.copy()
    for c in ['Category', 'Tier', 'Platform', 'KPI']:
        weights_df[c] = weights_df[c].astype(str).str.strip()
    weights_df['Weights'] = pd.to_numeric(weights_df['Weights'], errors='coerce')
    
    unknown_kpis = set(weights_df['KPI'].unique()) - ALLOWED_KPIS
    if unknown_kpis:
        st.warning(f"Ignored KPIs in weights_df (not used anymore): {sorted(list(unknown_kpis))}")
    
    # ===================== SESSION STATE =====================
    def zero_inputs():
        return {t: 0 for t in TIERS}
    
    if 'inputs_a' not in st.session_state:
        st.session_state.inputs_a = zero_inputs()
    if 'inputs_b' not in st.session_state:
        st.session_state.inputs_b = zero_inputs()
    if 'inputs_c' not in st.session_state:
        st.session_state.inputs_c = zero_inputs()
    
    available_categories = sorted(weights_df['Category'].dropna().unique().tolist())
    if not available_categories:
        st.error("No categories found in weights_df.")
        st.stop()
    
    for k in ['category_a', 'category_b', 'category_c']:
        if k not in st.session_state:
            st.session_state[k] = available_categories[0]
    
    def platforms_for_category(cat):
        return sorted(weights_df.loc[weights_df['Category'] == cat, 'Platform'].dropna().unique().tolist())
    
    if 'platform_a' not in st.session_state:
        ps = platforms_for_category(st.session_state.category_a)
        st.session_state.platform_a = ps[0] if ps else None
    if 'platform_b' not in st.session_state:
        ps = platforms_for_category(st.session_state.category_b)
        st.session_state.platform_b = ps[0] if ps else None
    if 'platform_c' not in st.session_state:
        ps = platforms_for_category(st.session_state.category_c)
        st.session_state.platform_c = ps[0] if ps else None
    
    # ===================== HELPERS =====================
    def get_weights(category, platform, kpi):
        if platform is None or kpi not in ALLOWED_KPIS:
            return {}
        sub = weights_df.loc[
            (weights_df['Category'] == category) &
            (weights_df['Platform'] == platform) &
            (weights_df['KPI'] == kpi),
            ['Tier', 'Weights']
        ].copy()
        if sub.empty:
            return {}
        sub['Weights'] = pd.to_numeric(sub['Weights'], errors='coerce')
        return {row['Tier']: 0.0 if pd.isna(row['Weights']) else float(row['Weights']) for _, row in sub.iterrows()}
    
    def colored_percentage(p):
        if p >= 40:
            return f"<span style='color:#1E90FF;font-weight:bold;'>{p:.1f}%</span>"
        elif p >= 20:
            return f"<span style='color:#FF9800;font-weight:bold;'>{p:.1f}%</span>"
        elif p > 0:
            return f"<span style='color:#009688;'>{p:.1f}%</span>"
        else:
            return "<span style='color:#aaa;'>0.0%</span>"
    
    def safe_div(n, d):
        return (n / d) if d not in (0, None) else 0.0
    
    # ===================== INPUT PANELS =====================
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
            options = plats if plats else ['(None)']
            current = st.session_state.get(plat_key, options[0])
            if current not in options:
                current = options[0]
            selected = st.selectbox(
                f"Simulation {sim_key.upper()} - Platform:",
                options,
                key=f"plat_{sim_key}",
                index=options.index(current)
            )
            st.session_state[plat_key] = None if selected == '(None)' else selected
    
            new_inputs = {}
            # Keep tier order stable
            for t in TIERS:
                c1, c2 = st.columns([3, 2])
                val = c1.number_input(f"{t}", min_value=0, value=st.session_state[inputs_key][t], key=f"{sim_key}_{t}")
                new_inputs[t] = val
                total_new = sum(new_inputs.values())
                percent = (val / total_new) * 100 if total_new > 0 else 0
                c2.markdown(colored_percentage(percent), unsafe_allow_html=True)
    
            st.session_state[inputs_key] = new_inputs
    
            total_final = sum(new_inputs.values())
            st.markdown(
                f"""
                <div style="background:{bg_color};padding:14px 0;border-radius:12px;text-align:center;box-shadow:0 2px 5px #00000022;">
                    <div style="font-size:2.2rem;font-weight:900;color:{title_color};">{total_final:,}</div>
                    <div style="font-size:1.1rem;">💰 Total Budget {sim_key.upper()}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    inputs_panel(col_input_a, 'a', 'category_a', 'platform_a', 'inputs_a', '#e0f7fa', '#0277bd')
    inputs_panel(col_input_b, 'b', 'category_b', 'platform_b', 'inputs_b', '#f3e5f5', '#8e24aa')
    inputs_panel(col_input_c, 'c', 'category_c', 'platform_c', 'inputs_c', '#e8f5e9', '#2e7d32')
    
    # ===================== SIMULATION (Impression/View/Engagement/Share only) =====================
    def calc_metrics(inputs, category, platform):
        w_imp   = get_weights(category, platform, "Impression")
        w_view  = get_weights(category, platform, "View")
        w_eng   = get_weights(category, platform, "Engagement")
        w_share = get_weights(category, platform, "Share")
    
        tot_imp   = sum(inputs.get(k, 0) * w_imp.get(k, 0)   for k in inputs)
        tot_view  = sum(inputs.get(k, 0) * w_view.get(k, 0)  for k in inputs)
        tot_eng   = sum(inputs.get(k, 0) * w_eng.get(k, 0)   for k in inputs)
        tot_share = sum(inputs.get(k, 0) * w_share.get(k, 0) for k in inputs)
        return tot_imp, tot_view, tot_eng, tot_share
    
    imp_a, view_a, eng_a, share_a = calc_metrics(st.session_state.inputs_a, st.session_state.category_a, st.session_state.platform_a)
    imp_b, view_b, eng_b, share_b = calc_metrics(st.session_state.inputs_b, st.session_state.category_b, st.session_state.platform_b)
    imp_c, view_c, eng_c, share_c = calc_metrics(st.session_state.inputs_c, st.session_state.category_c, st.session_state.platform_c)
    
    budget_a = sum(st.session_state.inputs_a.values())
    budget_b = sum(st.session_state.inputs_b.values())
    budget_c = sum(st.session_state.inputs_c.values())
    
    # Derived KPIs after simulate
    cpe_a, cpe_b, cpe_c               = safe_div(budget_a, eng_a), safe_div(budget_b, eng_b), safe_div(budget_c, eng_c)
    cpshare_a, cpshare_b, cpshare_c   = safe_div(budget_a, share_a), safe_div(budget_b, share_b), safe_div(budget_c, share_c)
    
    # ===================== RESULTS TABLE (effects, scoped CSS) =====================
    st.markdown("---")
    st.subheader("📈 Simulation Results Comparison")
    
    colA, colB, colC = "#0277bd", "#8e24aa", "#2e7d32"
    
    st.markdown(dedent("""
    <style>
    #sim-res { margin-top:4px; }
    #sim-res table { width:96%; margin:6px auto 14px auto; border-collapse:separate; border-spacing:0 6px; }
    #sim-res thead th {
      padding:12px 12px; color:#0f172a; text-align:center; font-weight:900;
      background: linear-gradient(90deg, #f7faff, #eef2ff);
      border-top-left-radius:12px; border-top-right-radius:12px;
      position:relative; overflow:hidden;
    }
    #sim-res thead th.simA{ color:#0277bd; }
    #sim-res thead th.simB{ color:#8e24aa; }
    #sim-res thead th.simC{ color:#2e7d32; }
    #sim-res thead th::after{
      content:""; position:absolute; inset:0;
      background: linear-gradient(120deg, rgba(255,255,255,.7), transparent 30%, transparent 70%, rgba(255,255,255,.7));
      background-size: 200% 100%; animation: shine 4s linear infinite; opacity:.35; pointer-events:none;
    }
    #sim-res tbody td, #sim-res tbody th {
      background:#ffffff; border:1px solid #eaeef5; padding:8px 10px; color:#334155;
    }
    #sim-res tbody th { width:22%; font-weight:800; border-right:none; border-radius:10px 0 0 10px; }
    #sim-res tbody td { border-left:none; border-radius:0 10px 10px 0; position:relative; }
    
    #sim-res .cell { position:relative; padding: 6px 10px; }
    #sim-res .cell .bar {
      position:absolute; left:8px; top:50%; height:70%; transform:translateY(-50%);
      width: calc(var(--w, 0) * 1%); border-radius:10px;
      background: linear-gradient(90deg, var(--c), rgba(255,255,255,0));
      opacity:.20; filter:saturate(1.2); overflow:hidden;
    }
    #sim-res .cell .bar::after{
      content:""; position:absolute; inset:0;
      background: linear-gradient(120deg, rgba(255,255,255,.75), rgba(255,255,255,0) 30%, rgba(255,255,255,0) 70%, rgba(255,255,255,.75));
      background-size:200% 100%; animation: shine 3.6s linear infinite; opacity:.45;
    }
    #sim-res .cell .val { position:relative; z-index:1; font-weight:700; }
    #sim-res .cell.best .val { color: var(--c); text-shadow: 0 0 10px var(--c); }
    #sim-res .cell.tie  .val { color:#1e88e5; }
    #sim-res .cell .led {
      width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 10px var(--c);
      display:inline-block; margin-right:6px; vertical-align:middle; visibility:hidden;
    }
    #sim-res .cell.best .led { visibility:visible; }
    @keyframes shine { 0%{ background-position:200% 0; } 100%{ background-position:-200% 0; } }
    </style>
    """), unsafe_allow_html=True)
    
    def cells_with_effect(values, colors, decimals=0, low_better=False):
        a, b, c = values
        vmin, vmax = min(values), max(values)
        if vmax == vmin:
            pcts = [100 if v > 0 else 0 for v in values]
        else:
            if low_better:
                pcts = [(vmax - v) / (vmax - vmin) * 100 for v in values]
            else:
                pcts = [(v - vmin) / (vmax - vmin) * 100 for v in values]
        fmt = f"{{:,.{decimals}f}}"
    
        if low_better:
            best_val, cnt = vmin, [a, b, c].count(vmin)
            def klass(v): return "cell tie" if (v == best_val and cnt >= 2) else ("cell best" if v == best_val else "cell")
        else:
            best_val, cnt = vmax, [a, b, c].count(vmax)
            def klass(v): return "cell tie" if (v == best_val and cnt >= 2) else ("cell best" if v == best_val else "cell")
    
        cells = []
        for v, pct, col in zip([a, b, c], pcts, colors):
            disp = fmt.format(v)
            cells.append(
                f"<div class='{klass(v)}' style='--w:{pct:.1f};--c:{col};'><div class='bar'></div><span class='led'></span><span class='val'>{disp}</span></div>"
            )
        return tuple(cells)
    
    row_budget   = cells_with_effect((budget_a, budget_b, budget_c), (colA, colB, colC), decimals=0)
    row_imp      = cells_with_effect((imp_a,    imp_b,    imp_c   ), (colA, colB, colC), decimals=0)
    row_view     = cells_with_effect((view_a,   view_b,   view_c  ), (colA, colB, colC), decimals=0)
    row_eng      = cells_with_effect((eng_a,    eng_b,    eng_c   ), (colA, colB, colC), decimals=0)
    row_share    = cells_with_effect((share_a,  share_b,  share_c ), (colA, colB, colC), decimals=0)
    row_cpe      = cells_with_effect((cpe_a,    cpe_b,    cpe_c   ), (colA, colB, colC), decimals=2, low_better=True)
    row_cpshare  = cells_with_effect((cpshare_a,cpshare_b,cpshare_c), (colA, colB, colC), decimals=2, low_better=True)
    
    html_table = dedent(f"""
    <div id="sim-res">
    <table>
      <thead>
        <tr>
          <th></th>
          <th class="simA">Simulation A</th>
          <th class="simB">Simulation B</th>
          <th class="simC">Simulation C</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Category</th>
          <td>{st.session_state.category_a}</td>
          <td>{st.session_state.category_b}</td>
          <td>{st.session_state.category_c}</td>
        </tr>
        <tr>
          <th>Platform</th>
          <td>{st.session_state.platform_a if st.session_state.platform_a is not None else '-'}</td>
          <td>{st.session_state.platform_b if st.session_state.platform_b is not None else '-'}</td>
          <td>{st.session_state.platform_c if st.session_state.platform_c is not None else '-'}</td>
        </tr>
        <tr><th>Budget</th>        <td>{row_budget[0]}</td>   <td>{row_budget[1]}</td>   <td>{row_budget[2]}</td></tr>
        <tr><th>Impressions</th>   <td>{row_imp[0]}</td>      <td>{row_imp[1]}</td>      <td>{row_imp[2]}</td></tr>
        <tr><th>Views</th>         <td>{row_view[0]}</td>     <td>{row_view[1]}</td>     <td>{row_view[2]}</td></tr>
        <tr><th>Engagements</th>   <td>{row_eng[0]}</td>      <td>{row_eng[1]}</td>      <td>{row_eng[2]}</td></tr>
        <tr><th>Shares</th>        <td>{row_share[0]}</td>    <td>{row_share[1]}</td>    <td>{row_share[2]}</td></tr>
        <tr><th>CPE</th>           <td>{row_cpe[0]}</td>      <td>{row_cpe[1]}</td>      <td>{row_cpe[2]}</td></tr>
        <tr><th>CPShare</th>       <td>{row_cpshare[0]}</td>  <td>{row_cpshare[1]}</td>  <td>{row_cpshare[2]}</td></tr>
      </tbody>
    </table>
    </div>
    """)
    st.markdown(html_table, unsafe_allow_html=True)
    
    # ===================== CHARTS =====================
    st.markdown("#### ✨ Visual Comparison")
    
    metric_order = ["Budget", "Impressions", "Views", "Engagements", "Shares"]
    bar_df = pd.DataFrame([
        {"Simulation":"A","Metric":"Budget","Value":budget_a},
        {"Simulation":"B","Metric":"Budget","Value":budget_b},
        {"Simulation":"C","Metric":"Budget","Value":budget_c},
        {"Simulation":"A","Metric":"Impressions","Value":imp_a},
        {"Simulation":"B","Metric":"Impressions","Value":imp_b},
        {"Simulation":"C","Metric":"Impressions","Value":imp_c},
        {"Simulation":"A","Metric":"Views","Value":view_a},
        {"Simulation":"B","Metric":"Views","Value":view_b},
        {"Simulation":"C","Metric":"Views","Value":view_c},
        {"Simulation":"A","Metric":"Engagements","Value":eng_a},
        {"Simulation":"B","Metric":"Engagements","Value":eng_b},
        {"Simulation":"C","Metric":"Engagements","Value":eng_c},
        {"Simulation":"A","Metric":"Shares","Value":share_a},
        {"Simulation":"B","Metric":"Shares","Value":share_b},
        {"Simulation":"C","Metric":"Shares","Value":share_c},
    ])
    colors = {"A":"#0277bd","B":"#8e24aa","C":"#2e7d32"}
    
    sel = alt.selection_multi(fields=['Simulation'], bind='legend')
    bar = (
        alt.Chart(bar_df, height=330)
        .mark_bar(cornerRadius=5)
        .encode(
            x=alt.X('Metric:N', sort=metric_order, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Value:Q', title=''),
            color=alt.Color('Simulation:N',
                            scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())),
                            legend=alt.Legend(title="Sim")),
            opacity=alt.condition(sel, alt.value(1), alt.value(0.35)),
            tooltip=[alt.Tooltip('Simulation:N'), alt.Tooltip('Metric:N'), alt.Tooltip('Value:Q', format=',')]
        )
        .add_selection(sel)
    )
    text = bar.mark_text(dy=-6, color='#334155', fontWeight='bold').encode(
        text=alt.condition(alt.datum.Value > 0, alt.Text('Value:Q', format=',.0f'), alt.value(''))
    )
    st.altair_chart(bar + text, use_container_width=True)
    
    scatter_df = pd.DataFrame({
        "Simulation": ["A","B","C"],
        "CPE": [cpe_a, cpe_b, cpe_c],
        "CPShare": [cpshare_a, cpshare_b, cpshare_c],
        "Budget": [budget_a, budget_b, budget_c]
    })
    hover = alt.selection_single(on='mouseover', empty='all', fields=['Simulation'])
    scatter = (
        alt.Chart(scatter_df, height=330)
        .mark_circle(opacity=0.9)
        .encode(
            x=alt.X('CPE:Q', title='CPE (Budget / Engagements)'),
            y=alt.Y('CPShare:Q', title='CPShare (Budget / Shares)'),
            size=alt.Size('Budget:Q', legend=None, scale=alt.Scale(range=[60, 800])),
            color=alt.Color('Simulation:N',
                            scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())),
                            legend=alt.Legend(title="Sim")),
            opacity=alt.condition(hover, alt.value(1), alt.value(0.6)),
            tooltip=[
                alt.Tooltip('Simulation:N'),
                alt.Tooltip('Budget:Q', format=','),
                alt.Tooltip('CPE:Q', format=',.2f'),
                alt.Tooltip('CPShare:Q', format=',.2f'),
            ]
        )
        .add_selection(hover)
    )
    labels = alt.Chart(scatter_df).mark_text(dy=-10, fontWeight='bold').encode(
        x='CPE:Q', y='CPShare:Q', text='Simulation',
        color=alt.Color('Simulation:N',
                        scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())), legend=None)
    )
    st.altair_chart(scatter + labels, use_container_width=True)
    
    
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

    # ==========================
    # Load df_full (must exist)
    # ==========================
    if "df_full" in st.session_state:
        df_full = st.session_state["df_full"]
    elif "df_full" in globals():
        df_full = globals()["df_full"]
    else:
        st.error("df_full not found. Provide a DataFrame named 'df_full' with columns: kol_name, platform, tier, category, followers, cost, impression, engagement, view, share")
        st.stop()
    
    # ==========================
    # CSS for subtle shiny table (scoped)
    # ==========================
    st.markdown(dedent("""
    <style>
    #kol-res table{width:100%;border-collapse:separate;border-spacing:0 6px;margin:6px 0;}
    #kol-res thead th{
      padding:10px 10px; color:#0f172a; font-weight:900; text-align:left;
      background: linear-gradient(90deg,#f7faff,#eef2ff,#f7faff);
      background-size:200% 100%; animation: shine 7s linear infinite;
      border-top-left-radius:12px; border-top-right-radius:12px;
      border-bottom:1px solid #eaeef5;
    }
    #kol-res tbody td, #kol-res tbody th{
      background:#ffffff; border:1px solid #eaeef5; padding:8px 10px; color:#334155;
    }
    #kol-res tbody th{ width:16%; font-weight:800; border-right:none; border-radius:10px 0 0 10px; }
    #kol-res tbody td{ border-left:none; border-radius:0 10px 10px 0; }
    #kol-res tbody tr:nth-child(even) td, #kol-res tbody tr:nth-child(even) th{ background:#fafbff; }
    #kol-res tbody tr:hover td, #kol-res tbody tr:hover th{ background:#f1f5ff; }
    #kol-res td.num{ text-align:right; font-variant-numeric: tabular-nums; }
    #kol-res .best{ color:#0ea5e9; font-weight:900; text-shadow:0 0 8px rgba(14,165,233,.35); }
    #kol-res .total th, #kol-res .total td{
      background: linear-gradient(90deg, #e8f7ff, #f7fff5);
      border-color:#dbe7fb; font-weight:800;
    }
    @keyframes shine{ 0%{ background-position:200% 0; } 100%{ background-position:-200% 0; } }
    </style>
    """), unsafe_allow_html=True)
    
    # ==========================
    # Simplified pretty table renderer + download
    # ==========================
    def render_kol_table(df_in: pd.DataFrame, kpi_col: str, title: str = None, download_label: str = "Download CSV"):
        """
        - แสดงผลตารางแบบวิบวับอ่านง่าย (ไม่มีกราฟ)
        - เติมคอลัมน์ score ถ้ายังไม่มี (kpi/cost)
        - ไฮไลต์ค่าสูงสุดของ KPI หลัก (ยกเว้นแถว TOTAL)
        - มีปุ่มดาวน์โหลด CSV
        """
        if df_in is None or df_in.empty:
            st.info("No data to display.")
            return
    
        df = df_in.copy()
    
        # ensure numeric
        for c in ['cost','impression','engagement','view','share','score','followers']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
    
        # compute score if absent
        if 'score' not in df.columns and ('cost' in df.columns and kpi_col in df.columns):
            with pd.option_context('mode.use_inf_as_na', True):
                df['score'] = df[kpi_col] / df['cost']
    
        # order of columns to show
        display_cols = [c for c in ['category','kol_name','tier','platform','followers','cost','impression','engagement','view','share','score'] if c in df.columns]
        num_cols     = [c for c in ['followers','cost','impression','engagement','view','share','score'] if c in df.columns]
    
        # detect TOTAL row (from summarize_selection)
        total_mask = df.get('kol_name', pd.Series('', index=df.index)).astype(str).str.upper().eq('TOTAL')
    
        # max per numeric col excluding TOTAL
        max_map = {}
        base = df.loc[~total_mask, num_cols] if (~total_mask).any() else df[num_cols]
        for c in num_cols:
            s = pd.to_numeric(base[c], errors='coerce')
            mv = s.max(skipna=True)
            max_map[c] = float(mv) if pd.notna(mv) and np.isfinite(mv) else None
    
        # column pretty names
        pretty = {
            'category':'Category', 'kol_name':'KOL', 'tier':'Tier', 'platform':'Platform', 'followers':'Followers',
            'cost':'Cost', 'impression':'Impressions', 'engagement':'Engagements', 'view':'Views', 'share':'Shares', 'score':'Score'
        }
    
        def fmt_num(x, dec=0):
            try:
                return f"{float(x):,.{dec}f}" if dec>0 else f"{float(x):,.0f}"
            except Exception:
                return "-" if pd.isna(x) else str(x)
    
        if title:
            st.markdown(f"### {title}")
    
        # HTML build
        html = ["<div id='kol-res'><table><thead><tr>"]
        html += [f"<th>{pretty.get(h,h)}</th>" for h in display_cols]
        html.append("</tr></thead><tbody>")
    
        for idx, row in df.iterrows():
            tr_class = "total" if (('kol_name' in row) and str(row['kol_name']).upper()=='TOTAL') else ""
            html.append(f"<tr class='{tr_class}'>")
            for h in display_cols:
                if h not in num_cols:
                    # text-like cells
                    if h in ['category','kol_name','tier','platform']:
                        html.append(f"<th>{str(row.get(h)) if pd.notna(row.get(h)) else '-'}</th>")
                    else:
                        html.append(f"<td>{str(row.get(h))}</td>")
                else:
                    # numeric cells (right aligned)
                    v = row.get(h)
                    dec = 2 if h=='score' else 0
                    # highlight best value (exclude TOTAL)
                    is_best = False
                    mv = max_map.get(h, None)
                    if (not total_mask.iloc[idx]) and pd.notna(v) and mv is not None and np.isfinite(mv):
                        try:
                            is_best = abs(float(v) - mv) <= 1e-9
                        except Exception:
                            is_best = False
                    cls = "num best" if is_best else "num"
                    html.append(f"<td class='{cls}'>{fmt_num(v, dec)}</td>")
            html.append("</tr>")
        html.append("</tbody></table></div>")
        st.markdown("".join(html), unsafe_allow_html=True)
    
        # Download button (csv utf-8-sig for Excel)
        # include computed score in output
        out_df = df.copy()
        csv_bytes = out_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=download_label,
            data=csv_bytes,
            file_name=f"{(title or 'kol_result').replace(' ','_').lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # ==========================
    # Filters
    # ==========================
    st.header("🎯 KOL Selection Optimizer")
    
    # Tier
    all_tiers = ['All', 'VIP', 'Mega', 'Mid', 'Macro', 'Micro', 'Nano']
    if 'tier_selection' not in st.session_state:
        st.session_state.tier_selection = ['All']
    def update_tiers():
        selected = st.session_state['tier_multiselect']
        st.session_state.tier_selection = ['All'] if 'All' in selected else selected
    st.multiselect(
        "🏷️ Tier Selection", options=all_tiers, default=st.session_state.tier_selection,
        key='tier_multiselect', on_change=update_tiers
    )
    filtered_tiers = None if 'All' in st.session_state.tier_selection else [t.lower() for t in st.session_state.tier_selection]
    
    # Platform
    platform_column_exists = 'platform' in df_full.columns
    if platform_column_exists:
        platforms_raw = df_full['platform'].astype(str).str.strip().replace({'nan':'','None':'','NaN':''})
        unique_platforms = sorted([p for p in platforms_raw.unique().tolist() if p])
        all_platforms = ['All'] + unique_platforms
    else:
        all_platforms = ['All']
    if 'platform_selection' not in st.session_state:
        st.session_state.platform_selection = ['All']
    def update_platforms():
        selected = st.session_state['platform_multiselect']
        st.session_state.platform_selection = ['All'] if 'All' in selected else selected
    if platform_column_exists:
        st.multiselect(
            "🖥️ Platform Selection", options=all_platforms, default=st.session_state.platform_selection,
            key='platform_multiselect', on_change=update_platforms
        )
    else:
        st.info("No 'platform' column found; platform filtering is disabled.")
    filtered_platforms = None if ('All' in st.session_state.platform_selection or not platform_column_exists) else [p.lower() for p in st.session_state.platform_selection]
    
    # Category
    category_column_exists = 'category' in df_full.columns
    if category_column_exists:
        categories_raw = df_full['category'].astype(str).str.strip().replace({'nan':'','None':'','NaN':''})
        unique_categories = sorted([c for c in categories_raw.unique().tolist() if c])
        all_categories = ['All'] + unique_categories
    else:
        all_categories = ['All']
    if 'category_selection' not in st.session_state:
        st.session_state.category_selection = ['All']
    def update_categories():
        selected = st.session_state['category_multiselect']
        st.session_state.category_selection = ['All'] if 'All' in selected else selected
    if category_column_exists:
        st.multiselect(
            "📂 Category Selection", options=all_categories, default=st.session_state.category_selection,
            key='category_multiselect', on_change=update_categories
        )
    else:
        st.info("No 'category' column found; category filtering is disabled.")
    filtered_categories = None if ('All' in st.session_state.category_selection or not category_column_exists) else [c.lower() for c in st.session_state.category_selection]
    
    # ==========================
    # KPI map & helpers
    # ==========================
    kpi_map = {
        'total_impression': 'impression',
        'total_engagement': 'engagement',
        'total_view': 'view',
        'total_share': 'share',
    }
    
    def prepare_df(df_in: pd.DataFrame, kpi_col: str,
                   allowed_tiers=None, allowed_platforms=None, allowed_categories=None) -> pd.DataFrame:
        df_work = df_in.copy()
        for col in ['cost','impression','engagement','view','share','tier','platform','category','kol_name','followers']:
            if col not in df_work.columns:
                df_work[col] = pd.NA
        if allowed_tiers is not None:
            df_work = df_work[df_work['tier'].astype(str).str.lower().isin(allowed_tiers)]
        if allowed_platforms is not None:
            df_work = df_work[df_work['platform'].astype(str).str.lower().isin(allowed_platforms)]
        if allowed_categories is not None:
            df_work = df_work[df_work['category'].astype(str).str.lower().isin(allowed_categories)]
        for col in ['cost','impression','engagement','view','share','followers']:
            df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
        df_work = df_work[df_work['cost'].notna() & (df_work['cost'] > 0)]
        df_work = df_work[df_work[kpi_col].notna()]
        df_work = df_work.reset_index(drop=True)
        return df_work
    
    def summarize_selection(df_sel: pd.DataFrame) -> pd.DataFrame:
        if df_sel is None or df_sel.empty:
            return pd.DataFrame()
        summary = {
            'category': '',
            'kol_name': 'TOTAL' if 'kol_name' in df_sel.columns else '',
            'tier': '',
            'platform': '',
            'followers': '' if 'followers' in df_sel.columns else '',
            'cost': df_sel['cost'].sum() if 'cost' in df_sel else 0,
            'impression': df_sel['impression'].sum() if 'impression' in df_sel else 0,
            'engagement': df_sel['engagement'].sum() if 'engagement' in df_sel else 0,
            'view': df_sel['view'].sum() if 'view' in df_sel else 0,
            'share': df_sel['share'].sum() if 'share' in df_sel else 0,
            'score': ''
        }
        return pd.concat([df_sel, pd.DataFrame([summary])], ignore_index=True)
    
    # ==========================
    # Selectors (Greedy / LP)
    # ==========================
    def select_kols_greedy(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, allowed_categories=None):
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty:
            return pd.DataFrame()
        df_work['score'] = df_work[kpi_col] / df_work['cost']
        df_work = df_work.sort_values('score', ascending=False).reset_index(drop=True)
        selected_rows, total_cost = [], 0.0
        for _, row in df_work.iterrows():
            if len(selected_rows) >= k: break
            if total_cost + row['cost'] <= budget:
                selected_rows.append(row); total_cost += row['cost']
        return summarize_selection(pd.DataFrame(selected_rows))
    
    def greedy_multiple_scenarios(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, allowed_categories=None, num_scenarios=5):
        df_base = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_base.empty: return []
        scenarios, excluded_idx = [], set()
        for _ in range(num_scenarios):
            work = df_base.copy()
            if excluded_idx:
                work = work[~work.index.isin(excluded_idx)].reset_index(drop=True)
                if work.empty: break
            work['score'] = work[kpi_col] / work['cost']
            work = work.sort_values('score', ascending=False)
            selected_indices, selected_rows, total_cost = [], [], 0.0
            for i, row in work.iterrows():
                if len(selected_rows) >= k: break
                if total_cost + row['cost'] <= budget:
                    selected_rows.append(row); selected_indices.append(i); total_cost += row['cost']
            if not selected_rows: break
            scenarios.append(summarize_selection(pd.DataFrame(selected_rows)))
            work_chosen = work.loc[selected_indices].copy().sort_values('score', ascending=False)
            if not work_chosen.empty:
                key_cols = [c for c in ['kol_name','platform','cost'] if c in df_base.columns]
                if key_cols:
                    key_vals = tuple(work_chosen.iloc[0][key_cols].tolist())
                    mask = pd.Series(True, index=df_base.index)
                    for c, v in zip(key_cols, key_vals): mask &= (df_base[c] == v)
                    idx_to_exclude = df_base[mask].index.tolist()
                    if idx_to_exclude: excluded_idx.add(idx_to_exclude[0])
                else:
                    excluded_idx.add(work_chosen.index[0])
        return scenarios
    
    def optimize_kols_lp_single(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, allowed_categories=None, exact_k=False):
        try:
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        except Exception:
            st.error("PuLP not installed. Please: pip install pulp"); return pd.DataFrame()
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty: return pd.DataFrame()
        if len(df_work) > 200: df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
        n = len(df_work)
        prob = LpProblem("KOL_Selection", LpMaximize)
        x = [LpVariable(f"x_{i}", cat=LpBinary) for i in range(n)]
        prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
        prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
        prob += (lpSum(x[i] for i in range(n)) == k) if exact_k else (lpSum(x[i] for i in range(n)) <= k)
        status = prob.solve()
        try:
            if LpStatus[status] != 'Optimal': return pd.DataFrame()
        except Exception:
            pass
        chosen_idx = [i for i in range(n) if x[i].varValue == 1]
        return summarize_selection(df_work.loc[chosen_idx].copy())
    
    def optimize_kols_lp_multiple(df_in, budget, k, kpi_col, allowed_tiers=None, allowed_platforms=None, allowed_categories=None, num_scenarios=5, exact_k=False):
        try:
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, LpStatus
        except Exception:
            st.error("PuLP not installed. Please: pip install pulp"); return []
        df_work = prepare_df(df_in, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
        if df_work.empty: return []
        if len(df_work) > 200: df_work = df_work.nlargest(200, kpi_col).reset_index(drop=True)
        n = len(df_work); scenarios, cuts = [], []
        for s in range(num_scenarios):
            prob = LpProblem(f"KOL_Selection_{s+1}", LpMaximize)
            x = [LpVariable(f"x_{i}_{s}", cat=LpBinary) for i in range(n)]
            prob += lpSum(df_work.loc[i, kpi_col] * x[i] for i in range(n))
            prob += lpSum(df_work.loc[i, 'cost'] * x[i] for i in range(n)) <= budget
            prob += (lpSum(x[i] for i in range(n)) == k) if exact_k else (lpSum(x[i] for i in range(n)) <= k)
            for sel_set in cuts:
                prob += lpSum(x[i] for i in sel_set) <= max(0, len(sel_set) - 1)
            status = prob.solve()
            try:
                if LpStatus[status] != 'Optimal': break
            except Exception:
                pass
            chosen_idx = [i for i in range(n) if x[i].varValue == 1]
            if not chosen_idx: break
            cuts.append(set(chosen_idx))
            scenarios.append(summarize_selection(df_work.loc[chosen_idx].copy()))
        return scenarios
    
    # ==========================
    # UI Controls
    # ==========================
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selection_mode = st.radio("🔀 Optimization Method", ["Greedy", "Linear Programming"], horizontal=False)
    with col2:
        budget = st.number_input("💰 Total Budget (THB)", min_value=0, value=250000, step=1000)
    with col3:
        kpi_option = st.selectbox("📊 KPI Focus", options=['total_impression', 'total_engagement', 'total_view', 'total_share'])
    kpi_col = kpi_map[kpi_option]
    
    st.subheader("🧪 Scenario Mode")
    scenario_mode = st.radio("Choose scenario mode", ["By K values", "Multiple portfolios (same K)"], horizontal=True)
    
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
    
    # ==========================
    # Run Optimization
    # ==========================
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
                    if selection_mode == "Greedy":
                        res = select_kols_greedy(df_full, budget, k, kpi_col, allowed_tiers, allowed_platforms, allowed_categories)
                    else:
                        res = optimize_kols_lp_single(df_full, budget, k, kpi_col, allowed_tiers, allowed_platforms, allowed_categories, exact_k=exact_k)
                    if res.empty:
                        st.info(f"No feasible selection under budget for K={k}.")
                    else:
                        render_kol_table(res, kpi_col, title=f"Scenario K={k}", download_label=f"Download CSV (K={k})")
        else:
            st.success("✅ Optimization complete!")
            if selection_mode == "Greedy":
                scenarios = greedy_multiple_scenarios(df_full, budget, fixed_k, kpi_col, allowed_tiers, allowed_platforms, allowed_categories, num_scenarios=num_scenarios)
            else:
                scenarios = optimize_kols_lp_multiple(df_full, budget, fixed_k, kpi_col, allowed_tiers, allowed_platforms, allowed_categories, num_scenarios=num_scenarios, exact_k=exact_k)
            if not scenarios:
                st.warning("No feasible scenarios found. Try increasing budget or reducing K.")
            else:
                for i, sc in enumerate(scenarios, start=1):
                    render_kol_table(sc, kpi_col, title=f"Scenario #{i}", download_label=f"Download CSV (Scenario {i})")


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
    DISPLAY_ORDER = ['Nano', 'Micro', 'Mid', 'Macro', 'Mega', 'VIP']
    BIG_MAX = 1_000_000_000.0
    # Only 4 KPI from sheet; CPE/CPShare are derived after optimization
    KPI_CANON = ['Impression', 'View', 'Engagement', 'Share']
    
    # --------- Custom Errors ---------
    class NotEnoughDataError(Exception):
        pass
    
    # --------- Global tiny CSS for shine animation (scoped via Styler header) ---------
    st.markdown(dedent("""
    <style>
    @keyframes dfShine { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    </style>
    """), unsafe_allow_html=True)
    
    # --------- Helpers (weights / LP) ---------
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
    
        # Canonicalize KPI (exclude CPE/CPShare)
        kpi_map = {
            'impression': 'Impression', 'impressions': 'Impression', 'imp': 'Impression',
            'view': 'View', 'views': 'View',
            'engagement': 'Engagement', 'eng': 'Engagement',
            'share': 'Share', 'shares': 'Share'
        }
        df['KPI'] = df['KPI'].str.lower().map(kpi_map).fillna(df['KPI'])
        df = df[df['KPI'].isin(KPI_CANON)]
        return df
    
    def _platform_set(series):
        return sorted({str(x).strip() for x in series if str(x).strip() != ''})
    
    def _get_weights_for_kpi_lenient(df, category, kpi, agg='sum'):
        sub = df[(df['Category'] == category) & (df['KPI'] == kpi)]
        mp = {t: 0.0 for t in TIERS}
        if sub.empty:
            return mp, f"No rows for KPI='{kpi}' in Category='{category}'.", False
    
        platforms = _platform_set(sub['Platform'])
        # Aggregate across platforms
        grouped = sub.groupby('Tier', as_index=False)['Weights'].agg(agg)
        for _, row in grouped.iterrows():
            t = str(row['Tier']).strip()
            if t in mp:
                mp[t] = float(row['Weights'])
        has_any = any(v != 0.0 for v in mp.values())
    
        warn = None
        if not has_any:
            warn = f"No usable weights for KPI='{kpi}' in Category='{category}'."
        return mp, warn, has_any
    
    def _gather_kpi_maps_with_warnings(df, category, kpis=KPI_CANON):
        maps, warns = {}, []
        for k in kpis:
            m, w, _ = _get_weights_for_kpi_lenient(df, category, k)
            maps[k] = m
            if w: warns.append(w)
        warns = list(dict.fromkeys([w for w in warns if w]))
        return maps, warns
    
    def _build_weights_vector_for_priority_lenient(df, category, priority):
        p = str(priority).strip().lower()
        warnings = []
        if p == 'balanced':
            imap, iwarn, iok = _get_weights_for_kpi_lenient(df, category, 'Impression')
            vmap, vwarn, vok = _get_weights_for_kpi_lenient(df, category, 'View')
            emap, ewarn, eok = _get_weights_for_kpi_lenient(df, category, 'Engagement')
            for w in [iwarn, vwarn, ewarn]:
                if w: warnings.append(w)
            if not (iok or vok or eok):
                raise NotEnoughDataError(f"No usable weights for Impressions, Views, or Engagement in Category='{category}'.")
            w = [(imap[t] + vmap[t] + emap[t]) / 3.0 for t in TIERS]
            return np.array(w, float), ['Impression', 'View', 'Engagement'], warnings
        else:
            kpi_map = {
                'impression': 'Impression', 'impressions': 'Impression', 'imp': 'Impression',
                'view': 'View', 'views': 'View',
                'engagement': 'Engagement', 'eng': 'Engagement',
                'share': 'Share'
            }
            kpi_key = kpi_map.get(p, p)
            if kpi_key not in KPI_CANON:
                raise NotEnoughDataError(f"KPI '{priority}' is not available for optimization.")
            mp, warn, ok = _get_weights_for_kpi_lenient(df, category, kpi_key)
            if warn: warnings.append(warn)
            if not ok:
                raise NotEnoughDataError(warn or f"No usable weights for KPI='{kpi_key}' in Category='{category}'.")
            w = [mp[t] for t in TIERS]
            return np.array(w, float), [kpi_key], warnings
    
    def _compute_named_scores(x, kpi_maps):
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
        kpi_maps, warn_all = _gather_kpi_maps_with_warnings(df, category, KPI_CANON)
        warns.extend(warn_all)
        scores = _compute_named_scores(res.x, kpi_maps)
        return dict(
            x=res.x,
            weights_vec=weights_vec,
            used_kpis=used_kpis,
            primary_score=float(np.dot(res.x, weights_vec)),
            kpi_maps=kpi_maps,
            scores=scores
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
            scores = _compute_named_scores(x_vec, kpi_maps)  # 4 KPIs
            total_b = float(np.sum(list(alloc.values())))
            cpe = (total_b / scores['Engagement']) if scores['Engagement'] else 0.0
            cps = (total_b / scores['Share']) if scores['Share'] else 0.0
            scores_derived = dict(scores)
            scores_derived['CPE'] = cpe
            scores_derived['CPShare'] = cps
            return dict(
                label=label,
                allocation=alloc,
                primary_score=float(np.dot(x_vec, weights_vec)),
                scores=scores_derived
            )
    
        scenarios = [pack("Optimal", x_star)]
    
        # diversify within 1.5% tolerance
        eps_abs = abs(z_star) * 0.015
        A_ub = [-weights_vec]
        b_ub = [-(z_star - eps_abs)]
        for i, t in enumerate(TIERS):
            c = np.zeros(len(TIERS))
            c[i] = -1.0
            res = _solve_lp(c, total_budget, min_alloc, max_alloc, A_ub=A_ub, b_ub=b_ub)
            if res.success:
                scenarios.append(pack(f"Near-optimal (emphasize {t})", res.x))
    
        def key(s):
            return tuple(round(s['allocation'][t], 2) for t in TIERS)
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
        kpi_map = {
            'impression': 'Impression', 'impressions': 'Impression', 'imp': 'Impression',
            'view': 'View', 'views': 'View',
            'engagement': 'Engagement', 'eng': 'Engagement',
            'share': 'Share'
        }
        kpi_key = kpi_map.get(str(kpi_type).lower(), kpi_type)
        if kpi_key not in KPI_CANON:
            raise NotEnoughDataError(f"KPI '{kpi_type}' is not available for targeting.")
    
        w_map, warn, ok = _get_weights_for_kpi_lenient(df, category, kpi_key)
        if warn:
            warnings.append(warn)
        if not ok:
            raise NotEnoughDataError(warn or f"No usable weights for KPI='{kpi_key}' in Category='{category}'.")
    
        max_possible = sum(float(max_alloc[t]) * w_map.get(t, 0.0) for t in TIERS)
        if float(target_value) > max_possible + 1e-9:
            return [], warnings
    
        n = len(TIERS)
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
    
        kpi_maps, warn_all = _gather_kpi_maps_with_warnings(df, category, KPI_CANON)
        warnings.extend(warn_all)
    
        def pack(label, x):
            alloc = {TIERS[i]: float(x[i]) for i in range(n)}
            scores = _compute_named_scores(x, kpi_maps)  # 4 KPIs
            total_b = float(np.sum(list(alloc.values())))
            cpe = (total_b / scores['Engagement']) if scores['Engagement'] else 0.0
            cps = (total_b / scores['Share']) if scores['Share'] else 0.0
            scores_derived = dict(scores)
            scores_derived['CPE'] = cpe
            scores_derived['CPShare'] = cps
            achieved_target_kpi = float(sum(x[i] * w_map.get(TIERS[i], 0.0) for i in range(n)))
            return dict(
                label=label,
                allocation=alloc,
                required_budget=float(np.sum(x)),
                target_kpi_name=kpi_key,
                target_kpi_value=achieved_target_kpi,
                scores=scores_derived
            )
    
        scenarios = [pack("Target-Optimal (min budget)", x_star)]
    
        # variations within budget cap
        A_ub2 = [np.array([-w_map[t] for t in TIERS], float), np.ones(n, float)]
        b_ub2 = [-float(target_value), float(B_cap)]
        for i, t in enumerate(TIERS):
            c2 = np.zeros(n, float)
            c2[i] = -1.0
            res2 = _solve_lp_general(c2, A_ub=A_ub2, b_ub=b_ub2, bounds=bounds)
            if res2.success:
                scenarios.append(pack(f"Near-min (emphasize {t})", res2.x))
    
        def key(s):
            return tuple(round(s['allocation'][t], 2) for t in TIERS)
        uniq = {}
        for s in scenarios:
            uniq.setdefault(key(s), s)
        out = list(uniq.values())
        out.sort(key=lambda s: (s.get('required_budget', 0.0), -s['scores'].get(kpi_key, 0.0)))
        return out[:5], list(dict.fromkeys([w for w in warnings if w]))
    
    # ---------- Styler helpers ----------
    def _highlight_max(s):
        try:
            mx = s.max()
            return ['background-color: #d9fbe2; font-weight: 700' if v == mx else '' for v in s]
        except Exception:
            return [''] * len(s)
    
    def _highlight_min(s):
        try:
            mn = s.min()
            return ['background-color: #fff3d6; font-weight: 700' if v == mn else '' for v in s]
        except Exception:
            return [''] * len(s)
    
    def _style_header(styler):
        # Add gradient + subtle shine animation on header only (uses global keyframes dfShine)
        return styler.set_table_styles([
            {"selector": "th.col_heading",
             "props": [("background", "linear-gradient(90deg, #f7faff, #eef2ff, #f7faff)"),
                       ("background-size", "200% 100%"),
                       ("animation", "dfShine 8s linear infinite"),
                       ("color", "#0f172a"),
                       ("font-weight", "900"),
                       ("border-bottom", "1px solid #eaeef5")]}
        ])
    
    # ---------- UI ----------
    st.title("Budget Optimization Tool")
    
    # weights_df existence
    if "weights_df" in st.session_state:
        weights_df = st.session_state["weights_df"]
    elif "weights_df" in globals():
        weights_df = globals()["weights_df"]
    else:
        st.error("weights_df not found. Load it into a DataFrame named 'weights_df'.")
        st.stop()
    
    # Clean weights
    try:
        df_clean = _validate_and_prepare_weights(weights_df)
    except Exception as e:
        st.error(str(e))
        st.stop()
    
    # Mode selector
    mode = st.radio("Select optimization mode:", ["Maximize KPI (given budget)", "Achieve KPI target (min budget)"])
    
    # Clear state on mode change
    if 'mode_prev' not in st.session_state:
        st.session_state.mode_prev = mode
    elif mode != st.session_state.mode_prev:
        for k in list(st.session_state.keys()):
            if k.endswith('_max') or k.endswith('_tgt') or k.startswith('result_'):
                st.session_state.pop(k, None)
        st.session_state.mode_prev = mode
        _rerun()
    
    # Category
    cats = sorted(df_clean['Category'].dropna().unique().tolist())
    default_idx = cats.index("Total IPG") if "Total IPG" in cats else 0
    category = st.selectbox("Select Category:", options=cats, index=default_idx)
    
    # ---------- Render (stacked bar + results table) ----------
    def render_outputs(scenarios, scenario_ids, show_target_cols=False):
        # 1) Stacked bar: Allocation by Tier with vibrant colors and highlight via legend
        recs = []
        for i, s in enumerate(scenarios):
            for tier in DISPLAY_ORDER:
                recs.append({"Scenario": scenario_ids[i], "Tier": tier, "Allocation": float(s['allocation'].get(tier, 0.0))})
        chart_df = pd.DataFrame(recs)
        chart_df["TierOrder"] = chart_df["Tier"].map({t: i for i, t in enumerate(DISPLAY_ORDER)})
    
        tier_colors = ["#60a5fa", "#34d399", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4"]
        sel = alt.selection_multi(fields=['Tier'], bind='legend')
    
        chart = (
            alt.Chart(chart_df)
            .mark_bar(cornerRadius=5, stroke='white', strokeWidth=0.5)
            .encode(
                x=alt.X("Scenario:N", sort=scenario_ids, axis=alt.Axis(title=None)),
                y=alt.Y("Allocation:Q", stack="zero", title="Allocation (Budget)"),
                color=alt.Color("Tier:N",
                                sort=DISPLAY_ORDER,
                                scale=alt.Scale(domain=DISPLAY_ORDER, range=tier_colors),
                                legend=alt.Legend(title="Tier")),
                order=alt.Order("TierOrder:Q"),
                opacity=alt.condition(sel, alt.value(1), alt.value(0.35)),
                tooltip=[alt.Tooltip("Scenario:N"),
                         alt.Tooltip("Tier:N"),
                         alt.Tooltip("Allocation:Q", format=",.2f")]
            )
            .add_selection(sel)
            .properties(height=420)
        )
        st.altair_chart(chart, use_container_width=True)
    
        # 2) KPI summary table with derived CPE/CPShare
        rows = []
        for i, s in enumerate(scenarios):
            sc = s['scores']
            row = {
                "Scenario": scenario_ids[i],
                "Priority KPI Score": s.get('primary_score', 0.0),
                "Impressions": sc.get('Impression', 0.0),
                "Views": sc.get('View', 0.0),
                "Engagement": sc.get('Engagement', 0.0),
                "Share": sc.get('Share', 0.0),
                "CPE": sc.get('CPE', 0.0),
                "CPShare": sc.get('CPShare', 0.0),
            }
            if show_target_cols:
                row["Required Budget"] = s.get('required_budget', 0.0)
                row["Target KPI"] = s.get('target_kpi_name', '')
                row["Target KPI Achieved"] = s.get('target_kpi_value', 0.0)
            rows.append(row)
        kpi_df = pd.DataFrame(rows)
    
        fmt = {
            "Priority KPI Score": "{:,.2f}",
            "Impressions": "{:,.2f}",
            "Views": "{:,.2f}",
            "Engagement": "{:,.2f}",
            "Share": "{:,.2f}",
            "CPE": "{:,.2f}",
            "CPShare": "{:,.2f}",
            "Required Budget": "{:,.2f}",
            "Target KPI Achieved": "{:,.2f}",
        }
        max_cols = ["Priority KPI Score", "Impressions", "Views", "Engagement", "Share"]
        min_cols = ["CPE", "CPShare"]
        if show_target_cols:
            min_cols.append("Required Budget")
            max_cols.append("Target KPI Achieved")
    
        styled = _style_header(
            kpi_df.style
            .format(fmt)
            .apply(_highlight_max, subset=max_cols)
            .apply(_highlight_min, subset=min_cols)
        )
        st.dataframe(styled, hide_index=True, use_container_width=True)
    
    # ===================== Modes =====================
    if mode == "Maximize KPI (given budget)":
        total_budget = st.number_input("Total Budget", min_value=0.0, value=10000.0, step=100.0, key="total_budget_max")
        priority = st.selectbox(
            "Optimization Priority",
            ["balanced", "impressions", "views", "engagement", "share"],  # no cpe/cpshare
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
                render_outputs(scenarios, scenario_ids, show_target_cols=False)
    
    else:
        kpi_type = st.selectbox(
            "KPI to target",
            ["impressions", "views", "engagement", "share"],  # no cpe/cpshare
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
                render_outputs(scenarios, scenario_ids, show_target_cols=True)
