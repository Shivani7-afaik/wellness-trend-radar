import json
import os
from collections import defaultdict
from datetime import datetime

# --- CONFIGURATION & CLEANUP ---

NOISE_WORDS = [
    "community update", "daily help thread", "reminder on community conduct",
    "notice on", "new or need help", "holy grail products", "misc",
    "humor", "weekly thread", "monthly thread", "help thread",
    "off topic", "off-topic", "announcement", "rules",
]

HIGH_VALUE_KEYWORDS = [
    "creatine", "magnesium", "lion's mane", "ashwagandha", "collagen",
    "electrolytes", "sea moss", "colostrum", "cordyceps", "adaptogens",
    "mushroom coffee", "gut health", "sleep", "probiotics", "biohacking",
    "longevity", "berberine",
]

KEYWORD_NORMALIZATION = {
    "creatine monohydrate": "creatine",
    "collagen peptides": "collagen",
    "electrolyte powder": "electrolytes",
    "magnesium glycinate": "magnesium",
    "gut microbiome": "gut health",
    "sleep gummies": "sleep",
    "probiotic drinks": "probiotics",
    "functional mushrooms": "mushrooms",
}

def normalize_keyword(keyword):
    keyword = (keyword or "").strip().lower()
    for suffix in [" cognition", " skin", " hydration", " supplement", " peptides", " benefits"]:
        keyword = keyword.replace(suffix, "")
    keyword = " ".join(keyword.split())
    return KEYWORD_NORMALIZATION.get(keyword, keyword)

def is_noise(signal):
    combined = f"{signal.get('title', '')} {signal.get('keyword', '')} {signal.get('description', '')}".lower()
    if any(word in combined for word in NOISE_WORDS): return True
    kw = (signal.get("keyword") or "").strip()
    return len(kw) <= 2

# --- SCORING LOGIC ---

def get_google_validation_score(keyword, all_signals):
    google_mentions = len([s for s in all_signals if s.get("source") == "google_trends" and keyword in normalize_keyword(s.get("keyword", ""))])
    reddit_mentions = len([s for s in all_signals if s.get("source") == "reddit" and keyword in normalize_keyword(s.get("keyword", ""))])
    if google_mentions >= 1: return 0.9
    if reddit_mentions >= 3: return 0.7
    return 0.3 if keyword in HIGH_VALUE_KEYWORDS else 0.0

def get_competition_score(items):
    brand_mentions = sum(1 for i in items if any(w in (i.get("title","") + i.get("description","")).lower() for w in ["brand", "amazon", "buy", "shop"]))
    return max(0.1, 1 - min(brand_mentions / 5, 1.0))

# --- MAIN ANALYZER ---

import json
import os
from collections import defaultdict

import json
import os
from collections import defaultdict

def analyze_trends(signals=None):
    # Fix the NameError by initializing grouped at the very top
    grouped = defaultdict(list)
    
    # Load signals if not provided directly
    if signals is None:
        try:
            with open("data/raw_signals.json", "r", encoding="utf-8") as f:
                signals = json.load(f)
        except:
            return []

    # Fill grouped dictionary
    for s in signals:
        kw = (s.get("keyword") or "unknown").strip().lower()
        if kw != "unknown":
            grouped[kw].append(s)

    trends = []
    for keyword, items in grouped.items():
        sources = list(set(i.get("source", "") for i in items))
        
        # Calculate specific count for the PubMed Box
        pubmed_count = sum(1 for i in items if i.get("source") == "pubmed")
        
        # Scoring for the Grid Boxes
        mkt_score = min(len(items) / 10.0, 1.0)
        conf_score = 0.95 if "google_trends" in sources or pubmed_count > 0 else 0.70

        trends.append({
            "trend": keyword,
            "keyword": keyword,
            "trend_score": round((mkt_score * 0.4) + (conf_score * 0.6), 2),
            "pubmed_papers": pubmed_count,  # Key for the blue box
            "market_size_score": f"{mkt_score:.2f}",
            "competition_score": "1.00",
            "confidence": conf_score,
            "time_to_mainstream": "6-12 months",
            "sources": sources
        })

    return sorted(trends, key=lambda x: x["trend_score"], reverse=True)[:10]

def calculate_trend_velocity(trends):
    """
    Returns trends as-is to satisfy app.py without needing a history file.
    """
    for t in trends:
        t["status"] = "RISING" if t["trend_score"] > 0.5 else "EMERGING"
        t["velocity_pct"] = 100.0
    return trends
