import streamlit as st
import json

st.title("Wellness Trend Radar")

st.write("AI-powered system detecting emerging wellness trends in India.")

# load the generated opportunities
with open("data/startup_opportunities.json", "r") as f:
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