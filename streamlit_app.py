import os
import json
import streamlit as st
from collections import defaultdict

from trend_scraper import compile_signals
from research_scraper import fetch_pubmed_signals
from opportunity_generator import generate_opportunities

st.set_page_config(page_title="Wellness Trend Radar", layout="wide")

st.title("Wellness Trend Radar")
st.write("AI-powered system detecting emerging wellness trends in India.")

os.makedirs("data", exist_ok=True)

HIGH_VALUE_KEYWORDS = [
    "creatine",
    "magnesium glycinate",
    "lion's mane",
    "ashwagandha",
    "collagen",
    "electrolytes",
    "sea moss",
    "colostrum",
    "cordyceps",
    "adaptogens",
    "mushroom coffee",
    "gut microbiome",
    "probiotic drinks",
    "berberine",
    "sleep gummies"
]

NOISE_WORDS = [
    "community update",
    "daily help thread",
    "reminder on community conduct",
    "notice on",
    "new or need help",
    "holy grail products",
    "misc",
    "humor"
]


def is_noise(signal):
    title = (signal.get("title") or "").lower()
    keyword = (signal.get("keyword") or "").lower()

    for w in NOISE_WORDS:
        if w in title or w in keyword:
            return True

    return len(keyword.strip()) == 0


def clean_keyword(keyword):
    keyword = (keyword or "").strip().lower()
    replacements = [
        " cognition",
        " sleep",
        " stress",
        " skin",
        " hydration",
        " supplement",
        " immunity",
        " exercise",
        " metabolism",
        " melatonin",
        " peptides"
    ]
    for r in replacements:
        keyword = keyword.replace(r, "")
    return keyword.strip()


def analyze_trends_from_signals(signals):
    cleaned_signals = [s for s in signals if not is_noise(s)]

    grouped = defaultdict(list)
    for s in cleaned_signals:
        keyword = clean_keyword(s.get("keyword"))
        if keyword:
            grouped[keyword].append(s)

    trends = []

    for keyword, items in grouped.items():
        signal_count = len(items)
        sources = list(set(i.get("source", "") for i in items))
        source_count = len(sources)
        total_score = sum(i.get("score", 0) for i in items)

        velocity_score = min(signal_count / 5, 1.0)
        market_score = 1.0 if keyword in HIGH_VALUE_KEYWORDS else 0.5

        brand_mentions = 0
        for i in items:
            text = ((i.get("title") or "") + " " + (i.get("description") or "")).lower()
            if "brand" in text or "amazon" in text or "buy" in text or "product" in text:
                brand_mentions += 1

        competition_score = 1 - min(brand_mentions / 5, 1.0)

        # live validation based on actual multi-source overlap
        reddit_mentions = len([i for i in items if i.get("source") == "reddit"])
        pubmed_mentions = len([i for i in items if i.get("source") == "pubmed"])
        youtube_mentions = len([i for i in items if i.get("source") == "youtube"])

        if reddit_mentions >= 2 and pubmed_mentions >= 1:
            validation_score = 1.0
        elif pubmed_mentions >= 1 or reddit_mentions >= 2 or youtube_mentions >= 2:
            validation_score = 0.6
        elif keyword in HIGH_VALUE_KEYWORDS:
            validation_score = 0.3
        else:
            validation_score = 0.0

        early_stage_bonus = 0.2 if signal_count <= 8 else 0.05

        fad_penalty = 0
        if source_count < 2 and signal_count < 3:
            fad_penalty = 0.25

        final_score = (
            velocity_score * 0.30
            + market_score * 0.20
            + competition_score * 0.15
            + validation_score * 0.20
            + early_stage_bonus
            - fad_penalty
        )

        final_score = min(final_score, 1.0)

        if signal_count >= 1 and final_score >= 0.35:
            if signal_count <= 3:
                time_to_mainstream = "6–12 months"
            elif signal_count <= 6:
                time_to_mainstream = "3–6 months"
            else:
                time_to_mainstream = "Already trending"

            trends.append({
                "keyword": keyword,
                "signals": signal_count,
                "sources": sources,
                "total_score": total_score,
                "trend_score": round(final_score, 2),
                "market_score": round(market_score, 2),
                "competition_score": round(competition_score, 2),
                "velocity_score": round(velocity_score, 2),
                "time_to_mainstream": time_to_mainstream
            })

    trends = sorted(
        trends,
        key=lambda x: (x["trend_score"], x["signals"], x["total_score"]),
        reverse=True
    )[:10]

    return trends


def render_trends(opportunities):
    if not opportunities:
        st.warning("No opportunities generated from this live run.")
        return

    st.subheader("Top Emerging Trends")

    for t in opportunities:
        st.markdown(f"## {t['trend']}")
        st.write(f"**Trend Score:** {t.get('trend_score', 'N/A')}")
        st.write(f"**Signals detected:** {t.get('signals', 'N/A')}")
        st.write(f"**Sources:** {', '.join(t.get('sources', []))}")

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


if st.button("Run Trend Scan"):
    with st.spinner("Collecting and analyzing signals..."):
        scraper_signals = compile_signals()
        pubmed_signals = fetch_pubmed_signals()

        signals = scraper_signals + pubmed_signals

        with open("data/raw_signals.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)

        reddit_count = len([s for s in signals if s.get("source") == "reddit"])
        youtube_count = len([s for s in signals if s.get("source") == "youtube"])
        pubmed_count = len([s for s in signals if s.get("source") == "pubmed"])

        st.success("Trend scan complete.")
        st.write(f"**Live source counts:** Reddit = {reddit_count}, YouTube = {youtube_count}, PubMed = {pubmed_count}, Total = {len(signals)}")

        trends = analyze_trends_from_signals(signals)
        opportunities = generate_opportunities(trends)

        with open("data/startup_opportunities.json", "w", encoding="utf-8") as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)

        render_trends(opportunities)
else:
    st.info("Click 'Run Trend Scan' to generate fresh trend opportunities.")
