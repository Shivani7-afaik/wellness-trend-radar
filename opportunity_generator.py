import json
import os


def generate_opportunities(trends):
    opportunities = []

    for trend in trends:
        keyword = trend["keyword"]
        score = trend["trend_score"]
        signals = trend["signals"]
        sources = trend["sources"]
        market_score = trend.get("market_score", 0)
        competition_score = trend.get("competition_score", 0)
        velocity_score = trend.get("velocity_score", 0)

        opportunity = {
            "trend": keyword,
            "trend_score": score,
            "signals": signals,
            "sources": sources,
            "market_score": market_score,
            "competition_score": competition_score,
            "velocity_score": velocity_score,
            "opportunity_brief": {
                "why_it_matters": f"'{keyword}' is appearing repeatedly in wellness discussions and shows early signal momentum.",
                "evidence": {
                    "signals_detected": signals,
                    "source_count": len(sources),
                    "sources": sources,
                    "velocity_score": velocity_score,
                    "market_score": market_score,
                    "competition_score": competition_score
                },
                "product_recommendation": f"Explore a D2C product or content-led wellness offering around {keyword}.",
                "category_recommendation": f"Potential category: {keyword} supplements / functional wellness product.",
                "founder_action": f"Validate demand for '{keyword}' in India using Amazon, Google Trends, and YouTube before launching."
            }
        }

        opportunities.append(opportunity)

    os.makedirs("data", exist_ok=True)

    with open("data/startup_opportunities.json", "w", encoding="utf-8") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    print(f"{len(opportunities)} startup opportunities generated.")
    print("Saved to data/startup_opportunities.json")

    return opportunities