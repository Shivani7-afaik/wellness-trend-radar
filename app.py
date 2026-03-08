import os
import json

from report_generator import generate_report
from trend_scraper import compile_signals
from trend_analyzer import analyze_trends
from opportunity_generator import generate_opportunities
from research_scraper import fetch_pubmed_signals


def main():
    os.makedirs("data", exist_ok=True)

    print("STEP 1: Collecting signals...")
    try:
        signals = compile_signals()
    except Exception as e:
        print(f"Signal collection failed: {e}")
        signals = []

    print("STEP 1B: Collecting research signals...")
    try:
        pubmed_signals = fetch_pubmed_signals()
        print(f"Research signals added: {len(pubmed_signals)}")
    except Exception as e:
        print(f"Research signal collection failed: {e}")
        pubmed_signals = []

    signals.extend(pubmed_signals)

    # Save combined raw signals
    with open("data/raw_signals.json", "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)

    print(f"Total signals collected: {len(signals)}")

    print("STEP 2: Analyzing trends...")
    try:
        trends = analyze_trends()
    except Exception as e:
        print(f"Trend analysis failed: {e}")
        trends = []

    print("STEP 3: Generating opportunities...")
    try:
        opportunities = generate_opportunities(trends)
    except Exception as e:
        print(f"Opportunity generation failed: {e}")
        opportunities = []

    print("DONE")
    print(f"{len(opportunities)} opportunity briefs generated")

    try:
        generate_report(opportunities)
        print("Report generated successfully.")
    except Exception as e:
        print(f"Report generation failed: {e}")


if __name__ == "__main__":
    main()
