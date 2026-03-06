import json
from collections import defaultdict

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
    "gut health",
    "sleep gummies",
    "sleep optimization"
]


def is_noise(signal):
    title = (signal.get("title") or "").lower()
    keyword = (signal.get("keyword") or "").lower()

    for w in NOISE_WORDS:
        if w in title or w in keyword:
            return True

    if len(keyword.strip()) == 0:
        return True

    return False


print("Skipping Google Trends discovery for now...")
google_signals = []
print("Google Trends: 0 signals (used later for validation)")

def get_google_validation_score(keyword, signals):
    """
    Temporary validation score.
    Uses Reddit + YouTube + high-value keyword bonus
    until direct Google Trends keyword validation is added.
    """
    reddit_mentions = len([
        s for s in signals
        if s.get("source") == "reddit" and keyword in (s.get("keyword", "").lower())
    ])

    youtube_mentions = len([
        s for s in signals
        if s.get("source") == "youtube" and keyword in (
            (s.get("title", "") + " " + s.get("description", "")).lower()
        )
    ])

    pubmed_mentions = len([
        s for s in signals
        if s.get("source") == "pubmed" and keyword in (
            (s.get("keyword", "") + " " + s.get("title", "")).lower()
        )
    ])

    if reddit_mentions >= 3 and (youtube_mentions >= 1 or pubmed_mentions >= 2):
        return 1.0
    elif reddit_mentions >= 2 or youtube_mentions >= 2 or pubmed_mentions >= 2:
        return 0.6
    elif keyword in HIGH_VALUE_KEYWORDS:
        return 0.3
    return 0.0

def analyze_trends():
    with open("data/raw_signals.json", "r", encoding="utf-8") as f:
        signals = json.load(f)

    cleaned_signals = [s for s in signals if not is_noise(s)]

    grouped = defaultdict(list)

    for s in cleaned_signals:
        keyword = (s.get("keyword") or "").strip().lower()

# clean research phrases into product categories
        keyword = keyword.replace(" cognition", "")
        keyword = keyword.replace(" skin", "")
        keyword = keyword.replace(" hydration", "")
        keyword = keyword.replace(" supplement", "")
        keyword = keyword.replace(" peptides", "")
        keyword = keyword.replace(" stress", "")
        if keyword:
            grouped[keyword].append(s)


    trends = []

    for keyword, items in grouped.items():
        signal_count = len(items)
        source_count = len(set(i.get("source", "") for i in items))
        total_score = sum(i.get("score", 0) for i in items)

        velocity_score = min(signal_count / 5, 1.0)
        market_score = 1.0 if keyword in HIGH_VALUE_KEYWORDS else 0.5

        brand_mentions = 0
        for i in items:
            text = ((i.get("title") or "") + " " + (i.get("description") or "")).lower()
            if "brand" in text or "amazon" in text or "buy" in text or "product" in text:
                brand_mentions += 1

        competition_score = 1 - min(brand_mentions / 5, 1.0)

        google_validation_score = get_google_validation_score(keyword, cleaned_signals)

        if signal_count <= 8:
            early_stage_bonus = 0.2
        else:
            early_stage_bonus = 0.05

        fad_penalty = 0
        if source_count < 2 and signal_count < 3:
            fad_penalty = 0.25

        final_score = (
            velocity_score * 0.30
            + market_score * 0.20
            + competition_score * 0.15
            + google_validation_score * 0.20
            + early_stage_bonus
            - fad_penalty
        )
        final_score = min(final_score, 1.0)
        if signal_count >= 2 and final_score >= 0.40:

    # estimate how early the trend is
            if signal_count <= 3:
                time_to_mainstream = "6-12 months"
            elif signal_count <= 6:
                time_to_mainstream = "3-6 months"
            else:
                time_to_mainstream = "Already trending"

            trends.append({
                "keyword": keyword,
                "signals": signal_count,
                "sources": list(set(i.get("source", "") for i in items)),
                "total_score": total_score,
                "trend_score": round(final_score, 2),
                "market_score": round(market_score, 2),
                "competition_score": round(competition_score, 2),
                "velocity_score": round(velocity_score, 2),
                "google_validation_score": round(google_validation_score, 2),
                "fad_penalty": round(fad_penalty, 2),
                "time_to_mainstream": time_to_mainstream
            })

    trends = sorted(
        trends,
        key=lambda x: (x["trend_score"], x["signals"], x["total_score"]),
        reverse=True
    )

    trends = trends[:10]

    with open("data/trend_opportunities.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2, ensure_ascii=False)

    print(f"{len(trends)} emerging trends identified.")

    return trends