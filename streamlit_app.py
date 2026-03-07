import os
import json
import streamlit as st

from trend_scraper import compile_signals
from research_scraper import fetch_pubmed_signals
from trend_analyzer import analyze_trends
from opportunity_generator import generate_opportunities

st.title("Wellness Trend Radar")
st.write("AI-powered system detecting emerging wellness trends in India.")

os.makedirs("data", exist_ok=True)

if st.button("Run Trend Scan"):
    with st.spinner("Collecting and analyzing signals..."):
        signals = compile_signals()
        pubmed_signals = fetch_pubmed_signals()
        signals.extend(pubmed_signals)

        with open("data/raw_signals.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)

        trends = analyze_trends()
        opportunities = generate_opportunities(trends)

        st.success("Trend scan complete.")

if os.path.exists("data/startup_opportunities.json"):
    with open("data/startup_opportunities.json", "r", encoding="utf-8") as f:
        trends = json.load(f)

    for t in trends:
        st.subheader(t["trend"])
        st.write("Trend Score:", t["trend_score"])
        st.write("Signals detected:", t["signals"])
        st.write("Sources:", ", ".join(t["sources"]))
        st.write("Why it matters:")
        st.write(t["opportunity_brief"]["why_it_matters"])
        st.write("Opportunity:")
        st.write(t["opportunity_brief"]["product_recommendation"])
        st.divider()
else:
    st.info("No trend results found yet. Click 'Run Trend Scan' to generate them.")
