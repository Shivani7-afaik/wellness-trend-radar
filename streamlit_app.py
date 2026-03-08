import os
import json
from collections import defaultdict
from datetime import datetime
import pandas as pd
import streamlit as st

from trend_scraper import compile_signals
from research_scraper import fetch_pubmed_signals
from opportunity_generator import generate_opportunities

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Wellness Trend Radar",
    page_icon="🌿",
    layout="wide"
)

# Refined CSS for high visibility and high-contrast aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0f172a; } /* Deep Dark Background */
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Metric Visibility (Sky Blue on Dark) */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important; 
        font-weight: 800;
        font-size: 2.2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important; 
        font-size: 1rem !important;
    }

    /* Trend Cards */
    .trend-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        color: #1e293b;
    }
    
    .trend-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    /* Source Badges Fix */
    .source-tag {
        background: #f1f5f9;
        color: #1e293b;
        padding: 4px 10px;
        border-radius: 6px;
        margin-right: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        border: 1px solid #cbd5e1;
        display: inline-block;
    }

    .paper-tag {
        background: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        border: 1px solid #bae6fd;
        display: inline-block;
    }

    .intensity-badge {
        background: #0f172a;
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
    }

    .action-box {
        background: #fdf2f8;
        border-left: 5px solid #db2777;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Market Data Bar */
    .market-bar {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CORE LOGIC (TOP 15)
# =========================================================

def process_trends(signals):
    grouped = defaultdict(list)
    pubmed_map = {}
    
    for s in signals:
        kw = s.get("keyword", "unknown").lower()
        if s.get("source") == "pubmed":
            pubmed_map[kw] = s.get("pubmed_papers", 0)
        else:
            grouped[kw].append(s)
            
    trends_for_gen = []
    for kw, items in grouped.items():
        sources = list(set(i.get("source") for i in items))
        pubmed_count = pubmed_map.get(kw, 0)
        # Dynamic score logic
        intensity = min(0.3 + (len(sources) * 0.15) + (pubmed_count * 0.001), 1.0)
        
        trends_for_gen.append({
            "keyword": kw,
            "sources": sources,
            "pubmed_papers": pubmed_count,
            "trend_score": round(intensity, 2),
            "signals": len(items)
        })
        
    return sorted(trends_for_gen, key=lambda x: x['trend_score'], reverse=True)[:15]

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("Radar Control")
    st.info("Scanner: India Wellness 2026")
    
    run_scan = st.button("Run Deep Scan", use_container_width=True)
    
    st.divider()
    min_score = st.slider("Quality Threshold", 0.0, 1.0, 0.40)
    st.caption("Filters the top 15 trends based on momentum score.")

# =========================================================
# MAIN CONTENT
# =========================================================

st.markdown("""
<div class="hero-container">
    <h1 style='margin:0; font-size: 2.5rem;'>Wellness Trend Radar</h1>
    <p style='opacity:0.8; font-size:1.1rem;'>Identifying high-growth market gaps via Social & Research signals.</p>
</div>
""", unsafe_allow_html=True)

if run_scan:
    with st.spinner("Compiling Top 15 Trends..."):
        scraper_signals = compile_signals()
        discovered = list(set(s.get("keyword", "").lower() for s in scraper_signals if len(s.get("keyword","")) > 3))
        
        pubmed_signals = []
        for kw in discovered[:20]:
            count = fetch_pubmed_signals(kw)
            if count > 0:
                pubmed_signals.append({"source": "pubmed", "keyword": kw, "pubmed_papers": count})
        
        all_signals = scraper_signals + pubmed_signals
        analyzed_trends = process_trends(all_signals)
        opportunities = generate_opportunities(analyzed_trends)
        
        with open("data/latest_session.json", "w") as f:
            json.dump(opportunities, f)
    st.rerun()

# Display Results
if os.path.exists("data/latest_session.json"):
    with open("data/latest_session.json", "r") as f:
        opportunities = json.load(f)
    
    st.markdown("### Market Health Indices")
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Trends", len(opportunities))
    m2.metric("Avg. Intensity", f"{sum(o['trend_score'] for o in opportunities)/len(opportunities):.2f}")
    m3.metric("Research Depth", sum(o.get('pubmed_papers', 0) for o in opportunities))

    st.divider()

    for opp in opportunities:
        if opp['trend_score'] < min_score:
            continue
            
        with st.container():
            st.markdown(f"""
            <div class="trend-card">
                <div class="trend-header">
                    <span style="font-size:1.6rem; font-weight:800; color:#0f172a;">{opp['trend']}</span>
                    <span class="intensity-badge">Intensity: {opp['trend_score']}</span>
                </div>
                <div style="margin-bottom:12px;">
                    {" ".join([f"<span class='source-tag'>{s.upper()}</span>" for s in opp['sources']])}
                    <span class="paper-tag">📚 {opp['pubmed_papers']} PAPERS FOUND</span>
                </div>
                <p style="color:#475569; font-size:1rem; line-height:1.6;">{opp['opportunity_brief']['why_it_matters']}</p>
                <div class="action-box">
                    <strong style="color:#9d174d; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.5px;">Founder Strategy</strong><br/>
                    <span style="color:#1e293b; font-weight: 500;">{opp['opportunity_brief']['founder_action']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Market Data and Links (Integrated)
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.markdown(f"**ETA to Mainstream:** `{opp['opportunity_brief'].get('time_to_mainstream', '6-12 Months')}`")
            c2.markdown(f"**Clinical Context:** `{opp['pubmed_papers']} Research Papers`")
            c3.link_button("Market Links", opp['trend_link'], use_container_width=True)
            
            st.markdown("<br/>", unsafe_allow_html=True)
else:
    st.info("Radar idle. Click 'Run Deep Scan' to identify the top 15 wellness opportunities.")
