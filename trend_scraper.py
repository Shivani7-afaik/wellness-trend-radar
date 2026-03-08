import os
import json
from datetime import datetime, timedelta

import requests

try:
    from pytrends.request import TrendReq
    _pytrends_available = True
except ImportError:
    _pytrends_available = False

try:
    from youtubesearchpython import VideosSearch
    _youtube_search_python_available = True
except ImportError:
    _youtube_search_python_available = False


# =========================
# CONFIG
# =========================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

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

WELLNESS_KEYWORDS = [
    "wellness",
    "health",
    "fitness",
    "nutrition",
    "supplements",
    "biohacking",
    "longevity",
    "mental health",
    "skincare",
    "women's health",
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
    "cordyceps benefits",
]

REDDIT_SUBS = [
    "Biohackers",
    "Supplements",
    "Nutrition",
    "Fitness",
    "SkincareAddiction",
    "Longevity",
    "IndianSkincareAddicts",
    "Health",
    "Nootropics",
    "Ayurveda",
]

CATEGORY_MAP = {
    "nutrition": ["nutrition", "gut microbiome", "gut health", "protein water", "probiotic"],
    "supplements": [
        "supplement", "supplements", "nmn", "collagen", "creatine",
        "magnesium glycinate", "magnesium threonate", "magnesium citrate",
        "resveratrol", "electrolytes", "berberine", "adaptogens",
        "ashwagandha", "l-theanine", "coq10", "taurine", "glutathione",
        "peptides", "shilajit", "holy basil", "triphala",
    ],
    "skincare": [
        "skincare", "skincareaddiction", "indianskincareaddicts",
        "skin", "skin barrier", "skin hydration", "hair loss", "rosemary oil",
    ],
    "fitness": ["fitness", "cold therapy", "cold plunge", "recovery drink"],
    "longevity": ["longevity", "nmn", "resveratrol", "biohacking"],
    "mental health": ["mental health", "sleep optimization", "sleep gummies", "brain fog", "fatigue"],
    "women's health": ["women's health", "hormone balance"],
    "wellness tech": ["biohacking", "wellness tech"],
}
DEFAULT_CATEGORY = "wellness"

CACHE_DIR = "data"
GOOGLE_TRENDS_CACHE = os.path.join(CACHE_DIR, "google_trends_cache.json")
YOUTUBE_CACHE = os.path.join(CACHE_DIR, "youtube_cache.json")


# =========================
# HELPERS
# =========================

def guess_category(text):
    text = (text or "").lower()
    for category, terms in CATEGORY_MAP.items():
        for term in terms:
            if term.lower() in text:
                return category
    return DEFAULT_CATEGORY


def normalize_engagement(platform, upvotes=0, comments=0, likes=0, views=0, retweets=0, replies=0):
    if platform == "reddit":
        return min(1000, upvotes * 2 + comments * 5)
    if platform == "youtube":
        return min(1000, int(views // 1000) + likes * 2)
    if platform == "twitter":
        return min(1000, likes + retweets * 3 + replies * 4)
    if platform == "google_trends":
        return min(1000, int(upvotes * 10))
    return 0


def parse_view_count(view_text):
    if not view_text:
        return 0

    cleaned = (
        view_text.lower()
        .replace("views", "")
        .replace("view", "")
        .replace(",", "")
        .strip()
    )

    try:
        if "k" in cleaned:
            return int(float(cleaned.replace("k", "").strip()) * 1000)
        if "m" in cleaned:
            return int(float(cleaned.replace("m", "").strip()) * 1_000_000)
        if "b" in cleaned:
            return int(float(cleaned.replace("b", "").strip()) * 1_000_000_000)

        digits = "".join(ch for ch in cleaned if ch.isdigit())
        return int(digits) if digits else 0
    except Exception:
        return 0


def deduplicate_signals(signals):
    seen = set()
    unique = []

    for s in signals:
        key = (
            s.get("source", "").strip().lower(),
            s.get("keyword", "").strip().lower(),
            s.get("title", "").strip().lower(),
            s.get("url", "").strip().lower(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


def make_signal(source, keyword, title, description="", score=0, category=None, date="", url="", author="", extra=None):
    payload = {
        "source": source,
        "keyword": (keyword or "").lower().strip(),
        "title": title or "",
        "description": description or "",
        "score": int(score or 0),
        "category": category or guess_category(f"{keyword} {title} {description}"),
        "date": date or "",
        "url": url or "",
        "author": author or "",
    }
    if extra and isinstance(extra, dict):
        payload.update(extra)
    return payload


def ensure_data_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def save_cache(path, data):
    ensure_data_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Cache save failed for {path}: {e}")


def load_cache(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Cache load failed for {path}: {e}")
    return []


# =========================
# GOOGLE TRENDS
# =========================

def fetch_google_trends_pytrends():
    signals = []

    if not _pytrends_available:
        print("pytrends is not installed.")
        return signals

    pytrends = TrendReq(hl="en-IN", tz=330)

    for keyword in INGREDIENTS:
        try:
            pytrends.build_payload([keyword], timeframe="today 3-m", geo="IN")
            interest = pytrends.interest_over_time()

            if interest.empty or keyword not in interest.columns:
                continue

            values = interest[keyword].tolist()
            if not values:
                continue

            latest = int(values[-1])
            peak = int(max(values))
            avg_score = sum(values) / len(values)

            # slightly relaxed threshold
            if latest >= 10 or peak >= 25:
                signals.append(
                    make_signal(
                        source="google_trends",
                        keyword=keyword,
                        title=keyword,
                        description=f"Google Trends India interest over last 3 months. Latest={latest}, Peak={peak}, Avg={avg_score:.2f}",
                        score=peak,
                        date=datetime.utcnow().strftime("%Y-%m-%d"),
                        extra={"latest": latest, "peak": peak, "avg_score": round(avg_score, 2)},
                    )
                )

        except Exception as e:
            print(f"pytrends failed for '{keyword}': {e}")
            continue

    return signals


def fetch_google_trends_rss():
    import xml.etree.ElementTree as ET

    signals = []
    urls = [
        "https://trends.google.com/trending/rss?geo=IN",
        "https://trends.google.com/trending/rss?geo=IN&category=h",
    ]

    wellness_terms = set(INGREDIENTS + WELLNESS_KEYWORDS)

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

                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                date_text = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

                if not title:
                    continue

                lower_title = title.lower()

                if any(term.lower() in lower_title for term in wellness_terms):
                    signals.append(
                        make_signal(
                            source="google_trends",
                            keyword=title,
                            title=title,
                            description="Google Trends India RSS trending query",
                            score=40,
                            date=date_text,
                        )
                    )

        except Exception as e:
            print(f"Google Trends RSS failed: {e}")
            continue

    return signals


def fetch_google_trends():
    print("Trying Google Trends via pytrends...")
    signals = fetch_google_trends_pytrends()

    if signals:
        save_cache(GOOGLE_TRENDS_CACHE, signals)
        print(f"Google Trends (pytrends) worked: {len(signals)} signals")
        return signals

    print("pytrends returned no signals. Trying RSS fallback...")
    signals = fetch_google_trends_rss()

    if signals:
        save_cache(GOOGLE_TRENDS_CACHE, signals)
        print(f"Google Trends (RSS) worked: {len(signals)} signals")
        return signals

    print("RSS also failed or returned nothing. Loading cached Google Trends data...")
    cached = load_cache(GOOGLE_TRENDS_CACHE)
    print(f"Google Trends cache: {len(cached)} signals")
    return cached


# =========================
# REDDIT
# =========================

def fetch_reddit_data():
    import xml.etree.ElementTree as ET
    from urllib.parse import quote

    signals = []
    atom_ns = "{http://www.w3.org/2005/Atom}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WellnessTrendRadar/1.0)"}

    for sub in REDDIT_SUBS:
        url = f"https://www.reddit.com/r/{quote(sub)}/new/.rss"
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            entries = root.findall(f"{atom_ns}entry")

            for entry in entries:
                title_el = entry.find(f"{atom_ns}title")
                content_el = entry.find(f"{atom_ns}content")
                author_el = entry.find(f"{atom_ns}author/{atom_ns}name")
                link_el = entry.find(f"{atom_ns}link")
                updated_el = entry.find(f"{atom_ns}updated")

                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                description = content_el.text.strip() if content_el is not None and content_el.text else ""
                author = author_el.text.strip() if author_el is not None and author_el.text else ""
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                updated = updated_el.text.strip() if updated_el is not None and updated_el.text else ""

                if not title:
                    continue

                text_blob = f"{title} {description}".lower()

                if any(term.lower() in text_blob for term in INGREDIENTS) or any(
                    kw.lower() in text_blob for kw in WELLNESS_KEYWORDS
                ):
                    signals.append(
                        make_signal(
                            source="reddit",
                            keyword=title,
                            title=title,
                            description=description[:500],
                            score=20,
                            date=updated,
                            url=link,
                            author=author,
                        )
                    )

        except Exception as e:
            print(f"Reddit RSS failed for r/{sub}: {e}")
            continue

    return signals


# =========================
# YOUTUBE
# =========================

def fetch_youtube_api():
    signals = []

    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set.")
        return signals

    for query in YOUTUBE_QUERIES:
        try:
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 8,
                "order": "date",
                "regionCode": "IN",
                "relevanceLanguage": "en",
                "key": YOUTUBE_API_KEY,
            }

            search_resp = requests.get(search_url, params=search_params, timeout=20)
            search_resp.raise_for_status()
            search_items = search_resp.json().get("items", [])

            video_ids = [
                item.get("id", {}).get("videoId", "")
                for item in search_items
                if item.get("id", {}).get("videoId")
            ]

            stats_map = {}
            if video_ids:
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    "part": "statistics,contentDetails",
                    "id": ",".join(video_ids),
                    "key": YOUTUBE_API_KEY,
                }
                stats_resp = requests.get(stats_url, params=stats_params, timeout=20)
                stats_resp.raise_for_status()

                for item in stats_resp.json().get("items", []):
                    stats_map[item["id"]] = item

            for item in search_items:
                vid = item.get("id", {}).get("videoId", "")
                if not vid:
                    continue

                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                published_at = snippet.get("publishedAt", "")
                url = f"https://www.youtube.com/watch?v={vid}"

                stats_item = stats_map.get(vid, {})
                statistics = stats_item.get("statistics", {}) if stats_item else {}
                views = int(statistics.get("viewCount", 0) or 0)
                likes = int(statistics.get("likeCount", 0) or 0)

                combined_text = f"{query} {title} {description}".lower()

                if views > 300 or any(term.lower() in combined_text for term in INGREDIENTS):
                    signals.append(
                        make_signal(
                            source="youtube",
                            keyword=query,
                            title=title,
                            description=description,
                            score=normalize_engagement("youtube", views=views, likes=likes),
                            date=published_at,
                            url=url,
                            extra={"views": views, "likes": likes},
                        )
                    )

        except Exception as e:
            print(f"YouTube API failed for '{query}': {e}")
            continue

    return signals


def fetch_youtube_fallback():
    signals = []

    if not _youtube_search_python_available:
        print("youtube-search-python is not installed.")
        return signals

    for query in YOUTUBE_QUERIES:
        try:
            results = VideosSearch(query, limit=8).result().get("result", [])
        except Exception as e:
            print(f"YouTube fallback failed for '{query}': {e}")
            continue

        for item in results:
            title = item.get("title", "") or ""
            description = ""

            if item.get("descriptionSnippet"):
                description = " ".join(
                    x.get("text", "") for x in item.get("descriptionSnippet", [])
                )

            view_text = ""
            if item.get("viewCount"):
                view_text = item["viewCount"].get("short") or item["viewCount"].get("text") or ""

            views = parse_view_count(view_text)

            if not title:
                continue

            combined_text = f"{query} {title} {description}".lower()

            if views > 300 or any(term.lower() in combined_text for term in INGREDIENTS):
                signals.append(
                    make_signal(
                        source="youtube",
                        keyword=query,
                        title=title,
                        description=description,
                        score=normalize_engagement("youtube", views=views),
                        date=datetime.utcnow().strftime("%Y-%m-%d"),
                        url=item.get("link", ""),
                        extra={"views": views},
                    )
                )

    return signals


def fetch_youtube_trends():
    print("Trying YouTube via official API...")
    signals = fetch_youtube_api()

    if signals:
        save_cache(YOUTUBE_CACHE, signals)
        print(f"YouTube API worked: {len(signals)} signals")
        return signals

    print("YouTube API unavailable or empty. Trying fallback library...")
    signals = fetch_youtube_fallback()

    if signals:
        save_cache(YOUTUBE_CACHE, signals)
        print(f"YouTube fallback worked: {len(signals)} signals")
        return signals

    print("YouTube fallback also failed or returned nothing. Loading cached YouTube data...")
    cached = load_cache(YOUTUBE_CACHE)
    print(f"YouTube cache: {len(cached)} signals")
    return cached


# =========================
# OPTIONAL TWITTER STUB
# =========================

def fetch_twitter_data():
    print("Twitter/X disabled in this free-ish version.")
    return []


# =========================
# INGREDIENT FILTER
# =========================

def filter_ingredient_signals(all_signals):
    ingredient_signals = []

    for signal in all_signals:
        text = (signal.get("title", "") + " " + signal.get("description", "")).lower()

        for ingredient in INGREDIENTS:
            if ingredient.lower() in text:
                new_signal = dict(signal)
                new_signal["keyword"] = ingredient.lower()
                new_signal["category"] = guess_category(ingredient)
                ingredient_signals.append(new_signal)

    return ingredient_signals


# =========================
# MAIN
# =========================

def compile_signals():
    import pandas as pd

    all_signals = []

    print("Fetching Google Trends...")
    google_signals = fetch_google_trends()
    all_signals.extend(google_signals)
    print(f"Google Trends: {len(google_signals)} signals")

    print("Fetching Reddit...")
    reddit_signals = fetch_reddit_data()
    all_signals.extend(reddit_signals)
    print(f"Reddit: {len(reddit_signals)} signals")

    print("Fetching YouTube...")
    yt_signals = fetch_youtube_trends()
    all_signals.extend(yt_signals)
    print(f"YouTube: {len(yt_signals)} signals")

    print("Fetching Twitter/X...")
    tw_signals = fetch_twitter_data()
    all_signals.extend(tw_signals)
    print(f"Twitter/X: {len(tw_signals)} signals")

    ingredient_signals = filter_ingredient_signals(all_signals)
    print(f"Ingredient signals identified: {len(ingredient_signals)}")
    all_signals.extend(ingredient_signals)

    all_signals = deduplicate_signals(all_signals)
    all_signals = all_signals[:500]

    ensure_data_dir()

    with open("data/raw_signals.json", "w", encoding="utf-8") as f:
        json.dump(all_signals, f, indent=2, ensure_ascii=False)

    df = pd.DataFrame(all_signals)
    df.to_csv("data/signals.csv", index=False)

    print(f"Total signals saved: {len(all_signals)}")
    print("Files created:")
    print("data/raw_signals.json")
    print("data/signals.csv")

    return all_signals
