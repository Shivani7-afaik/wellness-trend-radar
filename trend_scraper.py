import os
import json
from datetime import datetime, timedelta

# The import below will fail if pytrends is not installed.
# To handle missing dependency gracefully:
try:
    from pytrends.request import TrendReq
    _pytrends_available = True
except ImportError:
    _pytrends_available = False

try:

    _praw_available = True
except ImportError:
    _praw_available = False

try:
    from youtubesearchpython import VideosSearch
    _youtube_available = True
except ImportError:
    _youtube_available = False

# Twitter scraping disabled due to Python 3.12 compatibility issues
_snscrape_available = False

# --- INGREDIENT MONITORING ---
INGREDIENTS = [
    "ashwagandha",
    "lion's mane",
    "cordyceps",
    "reishi",
    "collagen",
    "collagen peptides",
    "nmn",
    "resveratrol",
    "adaptogens",
    "electrolytes",
    "electrolyte powder",
    "hydration powder",
    "creatine",
    "creatine monohydrate",
    "magnesium glycinate",
    "magnesium threonate",
    "magnesium citrate",
    "berberine",
    "gut microbiome",
    "gut health",
    "sleep optimization",
    "sleep gummies",
    "melatonin",
    "l-theanine",
    "cold therapy",
    "cold plunge",
    "protein water",
    "probiotic drinks",
    "probiotic soda",
    "sea moss",
    "colostrum",
    "mushroom coffee",
    "functional mushrooms",
    "nootropics",
    "brain fog",
    "focus supplement",
    "longevity",
    "biohacking",
    "hair loss",
    "rosemary oil",
    "skin barrier",
    "skin hydration",
    "ayurveda",
    "triphala",
    "shilajit",
    "holy basil",
    "coq10",
    "taurine",
    "glutathione",
    "peptides",
    "protein supplement",
    "hydration salts",
    "women's health",
    "hormone balance",
    "fatigue",
    "recovery drink"
]
# --- KEYWORD QUERIES ---
WELLNESS_KEYWORDS = [
    "wellness", "health", "fitness", "nutrition", "supplements",
    "biohacking", "longevity", "mental health", "skincare", "women's health"
]
YOUTUBE_QUERIES = [
    "creatine benefits",
    "magnesium glycinate sleep",
    "ashwagandha benefits",
    "collagen peptides",
    "electrolyte powder",
    "lion's mane benefits",
    "gut health drinks",
    "sleep gummies",
    "sea moss benefits",
    "colostrum supplement",
    "mushroom coffee",
    "protein water",
    "probiotic drinks",
    "hydration powder",
    "cordyceps benefits"
]
TWITTER_QUERIES = [
    "wellness trends", "biohacking", "new supplements", "longevity",
    "gut health", "adaptogens", "functional mushrooms"
]
REDDIT_SUBS = [
    "Biohackers", "Supplements", "Nutrition", "Fitness", "SkincareAddiction",
    "Longevity", "IndianSkincareAddicts", "Health"
]

CATEGORY_MAP = {
    "nutrition": ["nutrition", "gut microbiome"],
    "supplements": [
        "supplement", "supplements", "NMN", "collagen", "creatine",
        "magnesium glycinate", "resveratrol", "electrolytes", "berberine", "adaptogens"
    ],
    "skincare": [
        "skincare", "skincareaddiction", "IndianSkincareAddicts", "skin"
    ],
    "fitness": ["fitness", "cold therapy"],
    "longevity": ["longevity", "NMN", "resveratrol"],
    "mental health": ["mental health", "sleep optimization"],
    "wellness tech": ["biohacking", "wellness tech"]
}
DEFAULT_CATEGORY = "wellness"

def guess_category(text):
    text = (text or "").lower()
    for c, terms in CATEGORY_MAP.items():
        for term in terms:
            if term in text:
                return c
    return DEFAULT_CATEGORY

def normalize_engagement(platform, upvotes=0, comments=0, likes=0, views=0, retweets=0, replies=0):
    """Normalize engagement score (0-1000) per platform."""
    if platform == "reddit":
        return min(1000, upvotes * 2 + comments * 5)
    elif platform == "youtube":
        return min(1000, int(views // 1000) + likes * 2)
    elif platform == "twitter":
        return min(1000, likes + retweets * 3 + replies * 4)
    elif platform == "google_trends":
        return min(1000, int(upvotes * 10))
    return 0

def fetch_google_trends():
    import requests
    import xml.etree.ElementTree as ET

    signals = []

    urls = [
        "https://trends.google.com/trending/rss?geo=IN",
        "https://trends.google.com/trending/rss?geo=IN&category=h",
    ]

    for url in urls:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                title_el = item.find("title")
                pub_el = item.find("pubDate")

                if title_el is None:
                    continue

                query = (title_el.text or "").strip()
                if not query:
                    continue

                lower_query = query.lower()

                wellness_terms = [
                    "health", "wellness", "fitness", "supplement", "vitamin",
                    "protein", "creatine", "collagen", "magnesium", "ashwagandha",
                    "gut", "sleep", "hydration", "electrolyte", "skin", "hair",
                    "longevity", "biohacking", "mushroom", "probiotic", "ayurveda"
                ]

                if any(term in lower_query for term in wellness_terms):
                    signals.append({
                        "source": "google_trends",
                        "keyword": lower_query,
                        "title": query,
                        "description": "Google Trends India daily trending query",
                        "score": 50,
                        "category": guess_category(lower_query),
                        "date": pub_el.text if pub_el is not None else ""
                    })

        except Exception as e:
            print(f"Google Trends RSS error: {e}")
            continue

    return signals

import requests

def fetch_reddit_data():
    signals = []

    subreddits = [
        "Supplements",
        "biohackers",
        "Ayurveda",
        "Nootropics",
        "SkincareAddiction"
    ]

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
        headers = {"User-agent": "trend-radar"}

        try:
            res = requests.get(url, headers=headers)
            data = res.json()

            for post in data["data"]["children"]:
                p = post["data"]

                signals.append({
                    "source": "reddit",
                    "keyword": p["title"],
                    "title": p["title"],
                    "description": p.get("selftext",""),
                    "score": p["score"]
                })

        except:
            continue

    return signals

def fetch_youtube_trends():
    signals = []

    if not _youtube_available:
        print("youtube-search-python is not installed. Skipping YouTube.")
        return signals

    for query in YOUTUBE_QUERIES:
        try:
            results = VideosSearch(query, limit=10).result().get("result", [])
        except Exception:
            continue

        for r in results:
            title = r.get("title", "")
            description = ""
            if r.get("descriptionSnippet"):
                description = " ".join(
                    [x.get("text", "") for x in r.get("descriptionSnippet", [])]
                )

            views = 0
            view_text = ""
            if r.get("viewCount"):
                view_text = r["viewCount"].get("short") or r["viewCount"].get("text") or ""

            if view_text:
                cleaned = view_text.lower().replace("views", "").replace("view", "").replace(",", "").strip()
                try:
                    if "k" in cleaned:
                        views = int(float(cleaned.replace("k", "").strip()) * 1000)
                    elif "m" in cleaned:
                        views = int(float(cleaned.replace("m", "").strip()) * 1000000)
                    else:
                        views = int("".join(ch for ch in cleaned if ch.isdigit()) or 0)
                except Exception:
                    views = 0

            # skip very weak/noisy results
            if not title:
                continue

            score = normalize_engagement("youtube", views=views, likes=0)

            if views > 500 or any(
                term in (title + " " + description).lower()
                for term in INGREDIENTS
            ):
                signals.append({
                    "source": "youtube",
                    "keyword": query.lower(),
                    "title": title,
                    "description": description,
                    "score": score,
                    "category": guess_category(query + " " + title + " " + description)
                })

    return signals

def fetch_twitter_data():
    signals = []
    if not _snscrape_available:
        print("snscrape is not installed. Skipping Twitter/X.")
        return signals
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    until = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    for query in TWITTER_QUERIES:
        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
                f'{query} since:{since} until:{until} lang:en').get_items()):
                if i >= 50:
                    break
                signals.append({
                    "source": "twitter",
                    "keyword": query,
                    "title": tweet.content[:80] + ("..." if len(tweet.content) > 80 else ""),
                    "description": tweet.content,
                    "engagement_score": normalize_engagement(
                        "twitter",
                        likes=tweet.likeCount,
                        retweets=tweet.retweetCount,
                        replies=tweet.replyCount
                    ),
                    "date": tweet.date.strftime("%Y-%m-%d"),
                    "url": f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                    "category": guess_category(query + " " + tweet.content)
                })
        except Exception:
            continue
    return signals

def filter_ingredient_signals(all_signals):
    ingredient_signals = []
    for s in all_signals:
        text = (s.get("title", "") + " " + s.get("description", "")).lower()
        for ingredient in INGREDIENTS:
            if ingredient.lower() in text:
                signal = dict(s)
                signal["keyword"] = ingredient
                signal["category"] = guess_category(ingredient)
                ingredient_signals.append(signal)
    return ingredient_signals

def compile_signals():
    import pandas as pd

    all_signals = []

    print("Skipping Google Trends discovery for now...")
    google_signals = []
    print("Google Trends: 0 signals (used later for validation)")

    print("Fetching Reddit...")
    reddit_signals = fetch_reddit_data()
    all_signals.extend(reddit_signals)
    print(f"Reddit: {len(reddit_signals)} signals")

    print("Fetching YouTube...")
    yt_signals = fetch_youtube_trends()
    all_signals.extend(yt_signals)
    print(f"YouTube: {len(yt_signals)} signals")

    print("Fetching Twitter...")
    tw_signals = fetch_twitter_data()
    all_signals.extend(tw_signals)
    print(f"Twitter: {len(tw_signals)} signals")

    ingredient_signals = filter_ingredient_signals(all_signals)
    print(f"Ingredient signals identified: {len(ingredient_signals)}")
    all_signals.extend(ingredient_signals)

    # limit
    all_signals = all_signals[:500]

    os.makedirs("data", exist_ok=True)

    # SAVE JSON
    with open("data/raw_signals.json", "w", encoding="utf-8") as f:
        json.dump(all_signals, f, indent=2, ensure_ascii=False)

    # SAVE CSV (NEW PART)
    df = pd.DataFrame(all_signals)
    df.to_csv("data/signals.csv", index=False)

    print(f"Total signals saved: {len(all_signals)}")
    print("Files created:")
    print("data/raw_signals.json")
    print("data/signals.csv")

    return all_signals

