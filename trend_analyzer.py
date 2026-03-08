import json
import os
from collections import defaultdict
from datetime import datetime


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
    "help thread",
    "off topic",
    "off-topic",
    "announcement",
    "rules",
]

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
    "sleep",
    "probiotics",
    "biohacking",
    "longevity",
    "berberine",
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
    "mushroom coffee": "mushroom coffee",
    "women's health": "hormone balance",
    "fatigue": "energy support",
    "recovery drink": "recovery",
}


def normalize_keyword(keyword):
    keyword = (keyword or "").strip().lower()

    # cleanup of common trailing research words
    for suffix in [
        " cognition",
        " skin",
        " hydration",
        " supplement",
        " supplements",
        " peptides",
        " stress",
        " immunity",
        " exercise",
        " metabolism",
        " melatonin",
        " benefits",
    ]:
        keyword = keyword.replace(suffix, "")

    keyword = " ".join(keyword.split())

    if keyword in KEYWORD_NORMALIZATION:
        return KEYWORD_NORMALIZATION[keyword]

    return keyword


def is_noise(signal):
    title = (signal.get("title") or "").lower()
    keyword = (signal.get("keyword") or "").lower()
    description = (signal.get("description") or "").lower()

    combined = f"{title} {keyword} {description}"

    for word in NOISE_WORDS:
        if word in combined:
            return True

    if len(keyword.strip()) == 0:
        return True

    # remove extra-short junk keywords
    if len(keyword.strip()) <= 2:
        return True

    return False


def safe_load_signals(path="data/raw_signals.json"):
    if not os.path.exists(path):
        print(f"Signal file not found: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Could not load signals: {e}")
        return []


def get_google_validation_score(keyword, signals):
    """
    Validation using actual google_trends signals if available.
    Fallback: Reddit + YouTube + PubMed support.
    """
    keyword = normalize_keyword(keyword)

    google_mentions = len([
        s for s in signals
        if s.get("source") == "google_trends"
        and keyword in normalize_keyword(s.get("keyword", ""))
    ])

    reddit_mentions = len([
        s for s in signals
        if s.get("source") == "reddit"
        and keyword in normalize_keyword(s.get("keyword", ""))
    ])

    youtube_mentions = len([
        s for s in signals
        if s.get("source") == "youtube"
        and keyword in normalize_keyword(
            (s.get("keyword", "") + " " + s.get("title", "") + " " + s.get("description", ""))
        )
    ])

    pubmed_mentions = len([
        s for s in signals
        if s.get("source") == "pubmed"
        and keyword in normalize_keyword(
            (s.get("keyword", "") + " " + s.get("title", "")).lower()
        )
    ])

    if google_mentions >= 2:
        return 1.0
    if google_mentions >= 1 and (youtube_mentions >= 1 or reddit_mentions >= 1):
        return 0.85
    if reddit_mentions >= 3 and (youtube_mentions >= 1 or pubmed_mentions >= 1):
        return 0.7
    if youtube_mentions >= 2 or pubmed_mentions >= 2:
        return 0.55
    if keyword in HIGH_VALUE_KEYWORDS:
        return 0.3
    return 0.0


def get_market_score(keyword, items):
    keyword = normalize_keyword(keyword)

    if keyword in HIGH_VALUE_KEYWORDS:
        return 1.0

    # research-backed topics get a better market score
    pubmed_count = len([i for i in items if i.get("source") == "pubmed"])
    if pubmed_count >= 2:
        return 0.85
    if pubmed_count == 1:
        return 0.7

    return 0.5


def get_competition_score(items):
    """
    Lower score when there are too many direct product/brand-buy signals.
    """
    brand_mentions = 0

    for item in items:
        text = ((item.get("title") or "") + " " + (item.get("description") or "")).lower()

        if any(word in text for word in [
            "brand", "amazon", "buy", "product", "shop", "discount",
            "order now", "best brand", "top brand", "price"
        ]):
            brand_mentions += 1

    competition_score = 1 - min(brand_mentions / 5, 1.0)
    return max(0.1, competition_score)


def get_source_diversity_score(items):
    sources = set(i.get("source", "") for i in items if i.get("source"))
    return min(len(sources) / 4, 1.0)


def get_engagement_score(items):
    total_score = sum(int(i.get("score", 0) or 0) for i in items)

    # scale down to 0-1
    if total_score >= 1000:
        return 1.0
    if total_score >= 500:
        return 0.8
    if total_score >= 200:
        return 0.6
    if total_score >= 100:
        return 0.4
    if total_score >= 50:
        return 0.25
    return 0.1


def get_velocity_score(items):
    signal_count = len(items)
    source_count = len(set(i.get("source", "") for i in items if i.get("source")))

    base = min(signal_count / 5, 1.0)

    # small bonus for multiple sources
    if source_count >= 3:
        base += 0.15
    elif source_count == 2:
        base += 0.08

    return min(base, 1.0)


def estimate_time_to_mainstream(signal_count, source_count, google_validation_score):
    if signal_count <= 3:
        return "6-12 months"
    if signal_count <= 6:
        return "3-6 months"
    if source_count >= 3 and google_validation_score >= 0.7:
        return "Already trending"
    return "2-4 months"


def analyze_trends():
    signals = safe_load_signals("data/raw_signals.json")

    cleaned_signals = [s for s in signals if not is_noise(s)]

    grouped = defaultdict(list)

    for signal in cleaned_signals:
        keyword = normalize_keyword(signal.get("keyword") or "")
        if keyword:
            grouped[keyword].append(signal)

    trends = []

    for keyword, items in grouped.items():
        signal_count = len(items)
        source_count = len(set(i.get("source", "") for i in items if i.get("source")))
        total_score = sum(int(i.get("score", 0) or 0) for i in items)

        velocity_score = get_velocity_score(items)
        market_score = get_market_score(keyword, items)
        competition_score = get_competition_score(items)
        google_validation_score = get_google_validation_score(keyword, cleaned_signals)
        source_diversity_score = get_source_diversity_score(items)
        engagement_score = get_engagement_score(items)

        # early-stage boost
        if signal_count <= 8:
            early_stage_bonus = 0.15
        else:
            early_stage_bonus = 0.05

        # fad penalty
        fad_penalty = 0.0
        if source_count < 2 and signal_count < 3:
            fad_penalty = 0.25
        elif source_count < 2 and google_validation_score < 0.3:
            fad_penalty = 0.15

        final_score = (
            velocity_score * 0.22
            + market_score * 0.16
            + competition_score * 0.12
            + google_validation_score * 0.18
            + source_diversity_score * 0.16
            + engagement_score * 0.16
            + early_stage_bonus
            - fad_penalty
        )

        final_score = min(max(final_score, 0.0), 1.0)

        if signal_count >= 2 and final_score >= 0.35:
            time_to_mainstream = estimate_time_to_mainstream(
                signal_count,
                source_count,
                google_validation_score
            )

            trends.append({
                "keyword": keyword,
                "signals": signal_count,
                "sources": sorted(list(set(i.get("source", "") for i in items if i.get("source")))),
                "total_score": total_score,
                "trend_score": round(final_score, 2),
                "market_score": round(market_score, 2),
                "competition_score": round(competition_score, 2),
                "velocity_score": round(velocity_score, 2),
                "google_validation_score": round(google_validation_score, 2),
                "source_diversity_score": round(source_diversity_score, 2),
                "engagement_score": round(engagement_score, 2),
                "fad_penalty": round(fad_penalty, 2),
                "time_to_mainstream": time_to_mainstream
            })

    trends = sorted(
        trends,
        key=lambda x: (x["trend_score"], x["signals"], x["total_score"]),
        reverse=True
    )

    trends = trends[:10]

    os.makedirs("data", exist_ok=True)
    with open("data/trend_opportunities.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)

    print(f"{len(trends)} emerging trends identified.")

    return trends
