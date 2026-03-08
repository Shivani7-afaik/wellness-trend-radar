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
    layout="wide",
    initial_sidebar_state="expanded"
)

os.makedirs("data", exist_ok=True)


# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #f8fbff 0%, #f5f7fb 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        padding: 2rem;
        border-radius: 22px;
        color: white;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        line-height: 1.6;
    }

    .mini-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    .kpi-card {
        background: white;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    .kpi-label {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .section-heading {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .trend-card {
        background: white;
        border-radius: 20px;
        padding: 1.25rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .trend-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.4rem;
        text-transform: capitalize;
    }

    .trend-meta {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 0.7rem;
    }

    .pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 0.8rem;
        font-weight: 700;
        border: 1px solid #dbeafe;
    }

    .score-pill {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-size: 0.82rem;
        font-weight: 800;
        border: 1px solid #bbf7d0;
        margin-right: 0.5rem;
    }

    .soft-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-top: 0.7rem;
    }

    .small-label {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }

    .small-text {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .footer-note {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 1rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 0.8rem 1rem;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# CONSTANTS
# =========================================================
HIGH_VALUE_KEYWORDS = [
    "creatine",
    "magnesium",
    "lion's mane",
    "ashwagandha",
    "collagen",
    "electrolytes",
    "sea moss",
    "colostrum",
    "cordyceps",
    "adaptogens",
    "mushroom coffee",
    "gut health",
    "probiotics",
    "berberine",
    "sleep",
    "biohacking",
    "longevity"
]

NOISE_WORDS = [
    "community update",
    "daily help thread",
    "reminder on community conduct",
    "notice on",
    "new or need help",
    "holy grail products",
    "misc",
    "humor",
    "weekly thread",
    "monthly thread",
    "announcement"
]

KEYWORD_NORMALIZATION = {
    "creatine monohydrate": "creatine",
    "collagen peptides": "collagen",
    "electrolyte powder": "electrolytes",
    "hydration powder": "electrolytes",
    "hydration salts": "electrolytes",
    "magnesium glycinate": "magnesium",
    "magnesium threonate": "magnesium",
    "magnesium citrate": "magnesium",
    "gut microbiome": "gut health",
    "sleep gummies": "sleep",
    "sleep optimization": "sleep",
    "protein supplement": "protein",
    "probiotic drinks": "probiotics",
    "probiotic soda": "probiotics",
    "functional mushrooms": "mushrooms",
    "women's health": "hormone balance",
}


# =========================================================
# HELPERS
# =========================================================
def is_noise(signal):
    title = (signal.get("title") or "").lower()
    keyword = (signal.get("keyword") or "").lower()
    description = (signal.get("description") or "").lower()

    combined = f"{title} {keyword} {description}"

    for word in NOISE_WORDS:
        if word in combined:
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
        " supplements",
        " immunity",
        " exercise",
        " metabolism",
        " melatonin",
        " peptides",
        " benefits"
    ]

    for r in replacements:
        keyword = keyword.replace(r, "")

    keyword = " ".join(keyword.split())
    return KEYWORD_NORMALIZATION.get(keyword, keyword)


def analyze_trends_from_signals(signals):
    cleaned_signals = [s for s in signals if not is_noise(s)]

    grouped = defaultdict(list)
    for signal in cleaned_signals:
        keyword = clean_keyword(signal.get("keyword"))
        if keyword:
            grouped[keyword].append(signal)

    trends = []

    for keyword, items in grouped.items():
        signal_count = len(items)
        sources = sorted(list(set(i.get("source", "") for i in items if i.get("source"))))
        source_count = len(sources)
        total_score = sum(int(i.get("score", 0) or 0) for i in items)

        velocity_score = min(signal_count / 5, 1.0)
        market_score = 1.0 if keyword in HIGH_VALUE_KEYWORDS else 0.5

        brand_mentions = 0
        for item in items:
            text = ((item.get("title") or "") + " " + (item.get("description") or "")).lower()
            if any(word in text for word in ["brand", "amazon", "buy", "product", "shop", "price"]):
                brand_mentions += 1

        competition_score = 1 - min(brand_mentions / 5, 1.0)

        reddit_mentions = len([i for i in items if i.get("source") == "reddit"])
        pubmed_mentions = len([i for i in items if i.get("source") == "pubmed"])
        youtube_mentions = len([i for i in items if i.get("source") == "youtube"])
        google_mentions = len([i for i in items if i.get("source") == "google_trends"])

        if google_mentions >= 2:
            validation_score = 1.0
        elif google_mentions >= 1 and (youtube_mentions >= 1 or reddit_mentions >= 1):
            validation_score = 0.85
        elif reddit_mentions >= 2 and pubmed_mentions >= 1:
            validation_score = 0.75
        elif pubmed_mentions >= 1 or reddit_mentions >= 2 or youtube_mentions >= 2:
            validation_score = 0.6
        elif keyword in HIGH_VALUE_KEYWORDS:
            validation_score = 0.3
        else:
            validation_score = 0.0

        source_diversity_score = min(source_count / 4, 1.0)

        if total_score >= 1000:
            engagement_score = 1.0
        elif total_score >= 500:
            engagement_score = 0.8
        elif total_score >= 200:
            engagement_score = 0.6
        elif total_score >= 100:
            engagement_score = 0.4
        elif total_score >= 50:
            engagement_score = 0.25
        else:
            engagement_score = 0.1

        early_stage_bonus = 0.15 if signal_count <= 8 else 0.05

        fad_penalty = 0.0
        if source_count < 2 and signal_count < 3:
            fad_penalty = 0.25
        elif source_count < 2 and validation_score < 0.3:
            fad_penalty = 0.15

        final_score = (
            velocity_score * 0.22
            + market_score * 0.16
            + competition_score * 0.12
            + validation_score * 0.18
            + source_diversity_score * 0.16
            + engagement_score * 0.16
            + early_stage_bonus
            - fad_penalty
        )

        final_score = min(max(final_score, 0.0), 1.0)

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
                "google_validation_score": round(validation_score, 2),
                "source_diversity_score": round(source_diversity_score, 2),
                "engagement_score": round(engagement_score, 2),
                "time_to_mainstream": time_to_mainstream
            })

    trends = sorted(
        trends,
        key=lambda x: (x["trend_score"], x["signals"], x["total_score"]),
        reverse=True
    )[:10]

    return trends


def build_summary(signals, opportunities):
    source_counts = defaultdict(int)
    for s in signals:
        source_counts[s.get("source", "unknown")] += 1

    total_signals = len(signals)
    total_trends = len(opportunities)
    avg_trend_score = round(
        sum(float(o.get("trend_score", 0) or 0) for o in opportunities) / total_trends, 2
    ) if total_trends else 0

    top_source = max(source_counts.items(), key=lambda x: x[1])[0] if source_counts else "N/A"

    return {
        "total_signals": total_signals,
        "total_trends": total_trends,
        "avg_trend_score": avg_trend_score,
        "top_source": top_source,
        "source_counts": dict(source_counts)
    }


def render_source_badges(sources):
    if not sources:
        return "<span class='pill'>No source</span>"
    return " ".join([f"<span class='pill'>{s}</span>" for s in sources])


def render_opportunity_cards(opportunities, min_score=0.0, selected_source="All"):
    filtered = []
    for opp in opportunities:
        score = float(opp.get("trend_score", 0) or 0)
        sources = opp.get("sources", [])

        if score < min_score:
            continue
        if selected_source != "All" and selected_source not in sources:
            continue
        filtered.append(opp)

    if not filtered:
        st.warning("No trends match the selected filters.")
        return

    for idx, opp in enumerate(filtered, start=1):
        brief = opp.get("opportunity_brief", {})
        evidence = brief.get("evidence", {})

        st.markdown(f"""
        <div class="trend-card">
            <div class="trend-title">#{idx} {opp.get('trend', 'Unknown')}</div>
            <div class="trend-meta">
                <span class="score-pill">Trend Score: {opp.get('trend_score', 'N/A')}</span>
                <span class="pill">{opp.get('opportunity_type', 'Wellness opportunity')}</span>
            </div>
            <div>{render_source_badges(opp.get('sources', []))}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Signals", opp.get("signals", 0))
        col2.metric("Velocity", opp.get("velocity_score", 0))
        col3.metric("Market", opp.get("market_score", 0))
        col4.metric("Competition", opp.get("competition_score", 0))

        with st.expander("See full opportunity brief", expanded=False):
            st.markdown("**Why it matters**")
            st.write(brief.get("why_it_matters", "No summary available."))

            st.markdown("**Product recommendation**")
            st.write(brief.get("product_recommendation", "No product recommendation available."))

            st.markdown("**Category recommendation**")
            st.write(brief.get("category_recommendation", "No category recommendation available."))

            if brief.get("risk_note"):
                st.markdown("**Risk note**")
                st.write(brief.get("risk_note"))

            st.markdown("**Founder action**")
            st.write(brief.get("founder_action", "No founder action available."))

            st.markdown("**Evidence snapshot**")
            st.json(evidence)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


def load_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Wellness Trend Radar</div>
    <div class="hero-subtitle">
        AI-powered system for detecting emerging health and wellness trends in India using
        live digital signals, community discussions, video momentum, and research support.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Control Panel")
    st.write("Run a live scan or explore the latest saved results.")

    run_scan = st.button("Run Trend Scan", use_container_width=True)

    st.markdown("---")
    st.subheader("Filters")

    min_score_filter = st.slider(
        "Minimum Trend Score",
        min_value=0.0,
        max_value=1.0,
        value=0.35,
        step=0.05
    )

    source_filter = st.selectbox(
        "Source Filter",
        options=["All", "google_trends", "reddit", "youtube", "pubmed", "twitter", "instagram"],
        index=0
    )

    st.markdown("---")
    st.subheader("About")
    st.caption(
        "This app surfaces emerging wellness opportunities by combining social, search, "
        "video, and research signals into an opportunity-scoring pipeline."
    )


# =========================================================
# RUN OR LOAD DATA
# =========================================================
if run_scan:
    with st.spinner("Collecting and analyzing signals..."):
        scraper_signals = compile_signals()
        pubmed_signals = fetch_pubmed_signals()

        signals = scraper_signals + pubmed_signals

        with open("data/raw_signals.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)

        trends = analyze_trends_from_signals(signals)
        opportunities = generate_opportunities(trends)

        with open("data/startup_opportunities.json", "w", encoding="utf-8") as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False)

        st.success("Trend scan complete.")
else:
    signals = load_json_file("data/raw_signals.json", [])
    opportunities = load_json_file("data/startup_opportunities.json", [])
    if not signals and not opportunities:
        st.info("Click 'Run Trend Scan' from the sidebar to generate fresh trend opportunities.")


# =========================================================
# MAIN CONTENT
# =========================================================
if signals or opportunities:
    summary = build_summary(signals, opportunities)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Signals", summary["total_signals"])
    col2.metric("Emerging Trends", summary["total_trends"])
    col3.metric("Avg Trend Score", summary["avg_trend_score"])
    col4.metric("Top Source", summary["top_source"])

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Trend Opportunities",
        "Signal Overview",
        "Data Explorer",
        "Methodology"
    ])

    with tab1:
        st.markdown('<div class="section-heading">Top Emerging Trends</div>', unsafe_allow_html=True)
        render_opportunity_cards(
            opportunities,
            min_score=min_score_filter,
            selected_source=source_filter
        )

    with tab2:
        st.markdown('<div class="section-heading">Source Breakdown</div>', unsafe_allow_html=True)

        source_counts = summary["source_counts"]
        if source_counts:
            df_sources = pd.DataFrame(
                [{"Source": k, "Count": v} for k, v in source_counts.items()]
            ).sort_values("Count", ascending=False)

            st.bar_chart(df_sources.set_index("Source"))
            st.dataframe(df_sources, use_container_width=True)
        else:
            st.warning("No source data available yet.")

        st.markdown('<div class="section-heading">Top Signals Preview</div>', unsafe_allow_html=True)
        if signals:
            preview = pd.DataFrame(signals)
            keep_cols = [c for c in ["source", "keyword", "title", "score", "category", "date"] if c in preview.columns]
            st.dataframe(preview[keep_cols].head(50), use_container_width=True)
        else:
            st.info("No signals available.")

    with tab3:
        st.markdown('<div class="section-heading">Raw Opportunity Data</div>', unsafe_allow_html=True)
        if opportunities:
            st.json(opportunities)
        else:
            st.info("No opportunities available.")

        st.markdown('<div class="section-heading">Raw Signals Data</div>', unsafe_allow_html=True)
        if signals:
            st.json(signals[:100])
        else:
            st.info("No raw signals available.")

    with tab4:
        st.markdown('<div class="section-heading">How the system works</div>', unsafe_allow_html=True)

        st.markdown("""
        **1. Signal collection**  
        The app gathers wellness-related signals from supported sources such as Google Trends, Reddit, YouTube, and research data.

        **2. Signal cleaning**  
        Noise, repetitive community posts, and low-value items are filtered out. Similar phrases are normalized into clearer trend buckets.

        **3. Trend scoring**  
        Each trend is scored using:
        - signal volume
        - source diversity
        - validation strength
        - engagement
        - market relevance
        - competition intensity

        **4. Opportunity generation**  
        The system converts high-potential trends into startup-style opportunity briefs with product ideas, category suggestions, and founder actions.
        """)

        st.markdown("""
        <div class="soft-box">
            <div class="small-label">Note</div>
            <div class="small-text">
                This tool is designed for trend exploration and startup idea discovery.
                It should not be treated as medical advice, investment advice, or a substitute for detailed market research.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f"<div class='footer-note'>Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>",
        unsafe_allow_html=True
    )
