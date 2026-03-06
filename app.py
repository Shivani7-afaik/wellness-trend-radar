from report_generator import generate_report
from trend_scraper import compile_signals
from trend_analyzer import analyze_trends
from opportunity_generator import generate_opportunities
from research_scraper import fetch_pubmed_signals

def main():

    print("STEP 1: Collecting signals...")
    signals = compile_signals()
    print("STEP 1B: Collecting research signals...")
    pubmed_signals = fetch_pubmed_signals()
    signals.extend(pubmed_signals)

    import os
    import json
    os.makedirs("data", exist_ok=True)
    with open("data/raw_signals.json", "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)

    print(f"Research signals added: {len(pubmed_signals)}")

    print("STEP 2: Analyzing trends...")
    trends = analyze_trends()

    print("STEP 3: Generating opportunities...")
    opportunities = generate_opportunities(trends)

    print("DONE")
    print(f"{len(opportunities)} opportunity briefs generated")

    generate_report(opportunities)

if __name__ == "__main__":
    main()
    
