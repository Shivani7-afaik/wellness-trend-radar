import os
import json
import streamlit as st

from trend_scraper import compile_signals
from research_scraper import fetch_pubmed_signals
from trend_analyzer import analyze_trends
from opportunity_generator import generate_opportunities

st.set_page_config(page_title="Wellness Trend Radar", layout="wide")

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

        with open("data/startup_opportunities.json", "w", encoding="utf-8") as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)

    st.success("Trend scan complete.")

# Always try to show results if they exist
if os.path.exists("data/startup_opportunities.json"):
    try:
        with open("data/startup_opportunities.json", "r", encoding="utf-8") as f:
            trends = json.load(f)

        if trends:
            st.subheader("Top Emerging Trends")

            for t in trends:
                st.markdown(f"## {t['trend']}")
                st.write(f"**Trend Score:** {t['trend_score']}")
                st.write(f"**Signals detected:** {t['signals']}")
                st.write(f"**Sources:** {', '.join(t['sources'])}")

                if "time_to_mainstream" in t:
                    st.write(f"**Time to mainstream:** {t['time_to_mainstream']}")

                brief = t.get("opportunity_brief", {})
                evidence = brief.get("evidence", {})

                if evidence:
                    st.write("**Evidence:**")
                    st.write(
                        f"- Signals detected: {evidence.get('signals_detected', 'N/A')}\n"
                        f"- Source count: {evidence.get('source_count', 'N/A')}\n"
                        f"- Velocity score: {evidence.get('velocity_score', 'N/A')}\n"
                        f"- Market score: {evidence.get('market_score', 'N/A')}\n"
                        f"- Competition score: {evidence.get('competition_score', 'N/A')}"
                    )

                if "why_it_matters" in brief:
                    st.write("**Why it matters:**")
                    st.write(brief["why_it_matters"])

                if "product_recommendation" in brief:
                    st.write("**Opportunity:**")
                    st.write(brief["product_recommendation"])

                if "founder_action" in brief:
                    st.write("**Founder action:**")
                    st.write(brief["founder_action"])

                st.divider()
        else:
            st.warning("Scan finished, but no trends were generated.")
    except Exception as e:
        st.error(f"Could not load results: {e}")
else:
    st.info("No trend results yet. Click 'Run Trend Scan' to generate them.")
