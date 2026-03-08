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

# Custom CSS for a modern, "SaaS-style" aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #f8fafc; }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Trend Cards */
    .trend-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .trend-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .score-badge {
        background: #f0f9ff;
        color: #0369a1;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.9rem;
        border: 1px solid #bae6fd;
    }

    .action-box {
        background: #fdf2f8;
        border-left: 5px solid #db2777;
        padding: 1.25rem;
        border-radius: 12px;
        margin-top: 1rem;
    }

    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        font-weight: 800;
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CORE LOGIC UPGRADE
# =========================================================

def process_trends(signals):
    """
    Bridge function to clean signals and prepare them for opportunity generation.
    """
    # 1. Group signals by keyword
    grouped = defaultdict(list)
    pubmed_map = {}
    
    for s in signals:
        kw = s.get("keyword", "unknown").lower()
        if s.get("source") == "pubmed":
            pubmed_map[kw] = s.get("pubmed_papers", 0)
        else:
            grouped[kw].append(s)
            
    # 2. Build the Trend Objects
    trends_for_gen = []
    for kw, items in grouped.items():
        sources = list(set(i.get("source") for i in items))
        pubmed_count = pubmed_map.get(kw, 0)
        
        # Calculate dynamic intensity score (Fixes the 0.50 stuck issue)
        intensity = min(0.3 + (len(sources) * 0.15) + (pubmed_count * 0.001), 1.0)
        
        trends_for_gen.append({
            "keyword": kw,
            "sources": sources,
            "pubmed_papers": pubmed_count,
            "trend_score": round(intensity, 2),
            "signals": len(items)
        })
        
    return sorted(trends_for_gen, key=lambda x: x['trend_score'], reverse=True)

# =========================================================
# SIDEBAR & CONTROLS
# =========================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Radar Control")
    st.info("Scanner target: Indian Wellness Market (2026)")
    
    run_scan = st.button("🚀 Run Deep Scan", use_container_width=True)
    
    st.divider()
    min_score = st.slider("Quality Threshold", 0.0, 1.0, 0.4)
    st.caption("Higher thresholds filter for trends with validated research and multi-channel momentum.")

# =========================================================
# MAIN APP FLOW
# =========================================================

# Hero Section
st.markdown("""
<div class="hero-container">
    <h1 style='margin:0;'>Wellness Trend Radar</h1>
    <p style='opacity:0.8; font-size:1.1rem;'>Detecting health white-spaces using clinical research and social momentum.</p>
</div>
""", unsafe_allow_html=True)

if run_scan:
    with st.status("Initializing Radar...", expanded=True) as status:
        st.write("Gathering Social Signals (Reddit, YT, Google)...")
        scraper_signals = compile_signals()
        
        st.write("Polling PubMed Central for clinical validation...")
        # Get unique keywords discovered to search pubmed
        discovered = list(set(s.get("keyword", "").lower() for s in scraper_signals if len(s.get("keyword","")) > 3))
        
        pubmed_signals = []
        for kw in discovered[:12]: # Limit for speed
            count = fetch_pubmed_signals(kw)
            if count > 0:
                pubmed_signals.append({"source": "pubmed", "keyword": kw, "pubmed_papers": count})
        
        all_signals = scraper_signals + pubmed_signals
        
        st.write("Synthesizing Opportunities...")
        analyzed_trends = process_trends(all_signals)
        opportunities = generate_opportunities(analyzed_trends)
        
        # Save results
        with open("data/latest_session.json", "w") as f:
            json.dump(opportunities, f)
            
        status.update(label="Scan Complete!", state="complete", expanded=False)
    
    st.rerun()

# Load Data
if os.path.exists("data/latest_session.json"):
    with open("data/latest_session.json", "r") as f:
        opportunities = json.load(f)
else:
    opportunities = []

# Display Dashboard
if opportunities:
    # Top Level Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Trends", len(opportunities))
    m2.metric("Avg. Market Intensity", f"{sum(o['trend_score'] for o in opportunities)/len(opportunities):.2f}")
    m3.metric("Total Research Papers", sum(o.get('pubmed_papers', 0) for o in opportunities))

    st.divider()

    # Opportunity Cards
    for opp in opportunities:
        if opp['trend_score'] < min_score:
            continue
            
        with st.container():
            st.markdown(f"""
            <div class="trend-card">
                <div class="trend-header">
                    <span style="font-size:1.5rem; font-weight:800; color:#0f172a;">{opp['trend']}</span>
                    <span class="score-badge">Intensity: {opp['trend_score']}</span>
                </div>
                <div style="margin-bottom:1rem;">
                    {" ".join([f"<span style='background:#f1f5f9; padding:2px 8px; border-radius:5px; margin-right:5px; font-size:0.8rem;'>{s.upper()}</span>" for s in opp['sources']])}
                    <span style='background:#eef2ff; color:#4338ca; padding:2px 8px; border-radius:5px; font-size:0.8rem;'>📚 {opp['pubmed_papers']} PAPERS</span>
                </div>
                <p style="color:#475569; font-size:0.95rem; line-height:1.6;">{opp['opportunity_brief']['why_it_matters']}</p>
                <div class="action-box">
                    <strong style="color:#9d174d; font-size:0.8rem; text-transform:uppercase;">Founder Action</strong><br/>
                    <span style="color:#1e293b;">{opp['opportunity_brief']['founder_action']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View Market Data & Links"):
                c1, c2 = st.columns(2)
                c1.write(f"**Mainstream ETA:** {opp['opportunity_brief'].get('time_to_mainstream', '6-12 Months')}")
                c2.link_button("View Market Search", opp['trend_link'])
else:
    st.info("No data found. Click 'Run Deep Scan' to begin.")
