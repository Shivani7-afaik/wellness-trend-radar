import os
import json
from datetime import datetime
import time
import random
import requests
import pandas as pd

# Suppress pandas warnings
pd.set_option('future.no_silent_downcasting', True)

try:
    from pytrends.request import TrendReq
    _pytrends_available = True
except ImportError:
    _pytrends_available = False

# =========================
# CONFIG
# =========================
YOUTUBE_API_KEY = "AIzaSyDWTWMFbAaDjGpzaGQsyWsW7S3xEkhHqwM"

INGREDIENTS = ["ashwagandha", "lion's mane", "cordyceps", "reishi", "collagen", 
               "electrolytes", "creatine", "magnesium glycinate", "berberine", "sea moss"]

YOUTUBE_QUERIES = ["creatine benefits", "magnesium glycinate sleep", "ashwagandha benefits", "collagen peptides"]
REDDIT_SUBS = ["Biohackers", "Supplements", "Nutrition", "Longevity", "Health"]

# =========================
# HELPERS
# =========================
def make_signal(source, keyword, title, score=0):
    return {
        "source": source,
        "keyword": (keyword or "").lower().strip(),
        "title": title or "",
        "score": int(score or 0),
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    }

# =========================
# SCRAPERS
# =========================
def fetch_google_trends():
    if not _pytrends_available: return []
    signals = []
    test_keywords = random.sample(INGREDIENTS, 3) 
    pytrends = TrendReq(hl="en-IN", tz=330)
    for keyword in test_keywords:
        try:
            time.sleep(1)
            pytrends.build_payload([keyword], timeframe="today 3-m", geo="IN")
            interest = pytrends.interest_over_time()
            if not interest.empty:
                signals.append(make_signal("google_trends", keyword, f"GTrend: {keyword}", interest[keyword].max()))
        except: continue
    return signals

def fetch_youtube_api(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"part": "snippet", "q": query, "key": YOUTUBE_API_KEY, "maxResults": 3}
    try:
        data = requests.get(url, params=params, timeout=5).json()
        count = int(data.get("pageInfo", {}).get("totalResults", 0))
        return make_signal("youtube", query, f"YT: {query}", min(count, 100))
    except: return None

def fetch_reddit_signals():
    signals = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for sub in REDDIT_SUBS:
        try:
            # We pull the 25 hottest new posts
            url = f"https://www.reddit.com/r/{sub}/new/.json?limit=25"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                posts = response.json().get("data", {}).get("children", [])
                for post in posts:
                    title = post["data"]["title"]
                    # DISCOVERY: We treat the post title as a potential new trend
                    signals.append(make_signal("reddit", "discovery", title, 30))
            time.sleep(1)
        except: continue
    return signals

def fetch_twitter_signals():
    signals = []
    # Mocking Twitter/X mentions based on current Ingredient list
    for ing in random.sample(INGREDIENTS, 4):
        signals.append(make_signal("twitter", ing, f"X Post: {ing}", random.randint(10, 50)))
    return signals

# =========================
# MAIN COMPILE
# =========================
def compile_signals():
    os.makedirs("data", exist_ok=True)
    
    # 1. Google Trends
    gt_list = fetch_google_trends()
    
    # 2. YouTube
    yt_list = []
    for q in YOUTUBE_QUERIES:
        res = fetch_youtube_api(q)
        if res: yt_list.append(res)
        
    # 3. Reddit
    rd_list = fetch_reddit_signals()
    
    # 4. Twitter
    tw_list = fetch_twitter_signals()

    # Combine
    all_signals = gt_list + yt_list + rd_list + tw_list

    # Final Summary Output (Clean and No Symbols)
    print("Signal Collection Summary:")
    print(f"Google Trends signals: {len(gt_list)}")
    print(f"YouTube signals: {len(yt_list)}")
    print(f"Reddit signals: {len(rd_list)}")
    print(f"Twitter signals: {len(tw_list)}")
    print(f"Total signals saved: {len(all_signals)}")

    # Save
    with open("data/raw_signals.json", "w") as f: 
        json.dump(all_signals, f, indent=2)
    
    if all_signals:
        pd.DataFrame(all_signals).to_csv("data/signals.csv", index=False)

    return all_signals

if __name__ == "__main__":
    compile_signals()
