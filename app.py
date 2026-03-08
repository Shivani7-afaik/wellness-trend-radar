import os
import json
import pandas as pd
from report_generator import generate_report
from trend_scraper import compile_signals
from trend_analyzer import analyze_trends
from opportunity_generator import generate_opportunities
from research_scraper import fetch_pubmed_signals

# Suppress pandas warnings for a cleaner console
pd.set_option('future.no_silent_downcasting', True)

def main():
    os.makedirs("data", exist_ok=True)

    # --- STEP 1: Collection ---
    print("STEP 1: Collecting signals (Google, YouTube, Reddit, Twitter)...")
    try:
        signals = compile_signals()
    except Exception as e:
        print(f"Signal collection failed: {e}")
        signals = []
    
    discovered_keywords = set()
    for s in signals:
        kw = s.get("keyword", "").lower()
        if kw and len(kw) > 3: 
            discovered_keywords.add(kw)
    
    # --- STEP 1B: Research ---
    pubmed_signals = []
    pubmed_map = {} 

    print(f"STEP 1B: Researching {len(discovered_keywords)} discovered keywords in PubMed...")
    # Limit to top 15 discovered keywords
    for kw in list(discovered_keywords)[:15]:
        try:
            # fetch_pubmed_signals MUST return an integer count
            count = fetch_pubmed_signals(kw) 
            if count > 0:
                pubmed_map[kw.lower()] = count # Map lowercase for matching
                pubmed_signals.append({
                    "source": "pubmed",
                    "keyword": kw,
                    "paper_count": count
                })
        except Exception as e:
            print(f"Error researching {kw}: {e}")
            continue
    
    print(f"Research signals found: {len(pubmed_signals)}")
    signals.extend(pubmed_signals)

    # Save signals
    with open("data/raw_signals.json", "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)

    # --- STEP 2: Analysis ---
    print("STEP 2: Analyzing trends...")
    try:
        trends = analyze_trends()
        
        # MANUALLY INJECT PUBMED DATA INTO TRENDS
        for t in trends:
            kw_lookup = t.get("keyword", "").lower()
            # Inject the paper count from our map
            t['pubmed_papers'] = pubmed_map.get(kw_lookup, 0)
            if 'trend' not in t: 
                t['trend'] = t.get('keyword', 'Unknown')
                
    except Exception as e:
        print(f"Trend analysis failed: {e}")
        trends = []

    # --- STEP 3: Generation ---
    print("STEP 3: Generating opportunities...")
    try:
        if trends:
            opportunities = generate_opportunities(trends)
            generate_report(opportunities)
            print("DONE: Report generated successfully: trend_report.html")
        else:
            print("No trends identified.")
            
    except Exception as e:
        print(f"Final generation failed: {e}")

if __name__ == "__main__":
    main()
