import json
import os


CATEGORY_IDEAS = {
    "creatine": {
        "product": "a beginner-friendly creatine brand positioned around strength, recovery, and women-friendly education",
        "category": "sports nutrition / performance wellness",
        "action": "Test creator-led content around dosage, myths, and use cases for Indian consumers before building a product page."
    },
    "magnesium": {
        "product": "a sleep and stress-support supplement positioned around better recovery and nightly routines",
        "category": "sleep wellness / recovery supplements",
        "action": "Validate demand through sleep-focused content, landing pages, and keyword testing around stress, sleep, and recovery."
    },
    "ashwagandha": {
        "product": "a modern ayurvedic stress-support product with clean branding and research-backed education",
        "category": "stress relief / adaptogen supplements",
        "action": "Differentiate through trust, dosage transparency, and education instead of competing only on generic ayurveda branding."
    },
    "collagen": {
        "product": "a beauty-from-within supplement around skin, hair, and wellness routines",
        "category": "beauty wellness / ingestible skincare",
        "action": "Test whether the strongest pull is skin health, hair health, or premium beauty positioning before launch."
    },
    "electrolytes": {
        "product": "a hydration product focused on daily wellness, workouts, and heat-friendly Indian lifestyles",
        "category": "hydration / functional wellness drinks",
        "action": "Explore whether the strongest market is fitness users, general wellness users, or summer hydration use cases."
    },
    "gut health": {
        "product": "a gut-health brand built around probiotics, education, and digestive wellness habits",
        "category": "digestive wellness / functional nutrition",
        "action": "Start with educational content around bloating, digestion, and microbiome awareness, then test product interest."
    },
    "sleep": {
        "product": "a sleep-support offering combining supplements, routines, and content-led habit formation",
        "category": "sleep wellness / recovery",
        "action": "Test content on insomnia, stress, and bedtime rituals to learn whether users want supplements, education, or both."
    },
    "mushrooms": {
        "product": "a premium functional mushroom brand with a focus on energy, cognition, and modern wellness positioning",
        "category": "functional wellness / nootropics",
        "action": "Validate whether the strongest demand is around focus, immunity, or energy before choosing product format."
    },
    "mushroom coffee": {
        "product": "a content-led mushroom coffee or functional beverage brand for urban wellness consumers",
        "category": "functional beverages",
        "action": "Test taste acceptance, format preference, and willingness to switch from regular coffee before building inventory."
    },
    "cordyceps": {
        "product": "a performance and energy supplement positioned around stamina and recovery",
        "category": "sports performance / adaptogens",
        "action": "Check whether users respond more to exercise performance claims or everyday energy positioning."
    },
    "berberine": {
        "product": "a metabolic health supplement positioned around blood sugar awareness and wellness education",
        "category": "metabolic wellness / supplements",
        "action": "Be careful with claims and lead with education-first content before exploring product rollout."
    },
    "biohacking": {
        "product": "a content-led wellness brand curating products, routines, and tools for performance-focused consumers",
        "category": "wellness media / premium curation",
        "action": "Start as a content and community layer before deciding which product line deserves to be launched first."
    },
    "longevity": {
        "product": "a premium longevity-focused wellness brand built around education, supplements, and habit systems",
        "category": "preventive wellness / healthy aging",
        "action": "Position clearly for the Indian market, since longevity interest is rising but user education is still early."
    },
    "probiotics": {
        "product": "a gut-health beverage or supplement brand positioned around digestion and daily wellness routines",
        "category": "digestive health / functional foods",
        "action": "Test whether users prefer drinkable formats, capsules, or habit bundles before choosing the core offering."
    },
    "sea moss": {
        "product": "a niche superfood-led brand for early adopters interested in trend-driven wellness ingredients",
        "category": "superfoods / social-led wellness",
        "action": "Validate whether demand is real and sustained or mainly social-media driven before investing deeply."
    },
    "colostrum": {
        "product": "a premium immunity and recovery supplement for niche wellness users",
        "category": "premium supplements / immunity wellness",
        "action": "Assess whether the category has enough repeat-purchase potential in India before developing a full brand."
    },
    "adaptogens": {
        "product": "an adaptogen-led wellness line for stress, mood, and energy support",
        "category": "adaptogen supplements / modern ayurveda",
        "action": "Use strong education and trust-building because consumers may know the ingredients but not the category language."
    },
    "hormone balance": {
        "product": "a women-focused wellness brand around cycle health, energy, and hormonal support education",
        "category": "women’s health / functional wellness",
        "action": "Lead with education and community trust before moving into product claims or condition-specific positioning."
    },
}


def get_default_idea(keyword):
    return {
        "product": f"a D2C or content-led wellness offering around {keyword}",
        "category": f"{keyword} supplements / functional wellness",
        "action": f"Validate demand for '{keyword}' in India using search trends, creator content, and marketplace interest before launching."
    }


def choose_positioning(trend):
    keyword = trend["keyword"]
    return CATEGORY_IDEAS.get(keyword, get_default_idea(keyword))


def make_why_it_matters(keyword, signals, source_count, trend_score, velocity_score):
    if source_count >= 3 and trend_score >= 0.65:
        return f"'{keyword}' is showing strong cross-platform momentum, which suggests it may be moving from niche discussion into mainstream wellness demand."
    if velocity_score >= 0.7:
        return f"'{keyword}' is gaining momentum quickly and may represent an early but fast-rising wellness opportunity."
    if signals <= 3:
        return f"'{keyword}' is still early, but repeated appearances suggest it could become a breakout wellness theme if momentum continues."
    return f"'{keyword}' is appearing repeatedly in wellness conversations and shows credible early-stage demand."


def make_risk_note(competition_score, source_count, trend_score):
    if competition_score < 0.4:
        return "The category may already be crowded, so differentiation and branding will matter more than being first."
    if source_count < 2:
        return "This signal is still narrow, so it needs more validation before treating it as a major opportunity."
    if trend_score < 0.5:
        return "The signal is promising but still early, so demand should be validated carefully before investing in inventory."
    return "The opportunity looks promising, but execution quality and positioning will determine whether it becomes commercially viable."


def make_founder_action(keyword, base_action, source_count, market_score):
    if source_count >= 3 and market_score >= 0.8:
        return f"{base_action} Then shortlist one sharp customer segment and test pricing, product format, and messaging."
    if market_score >= 0.8:
        return f"{base_action} Also compare whether education-first or product-first positioning gets stronger traction."
    return f"{base_action} Use this phase to verify whether the trend has real buying intent or only curiosity."


def generate_opportunities(trends):
    opportunities = []

    for trend in trends:
        keyword = trend["keyword"]
        trend_score = trend["trend_score"]
        signals = trend["signals"]
        sources = trend["sources"]
        source_count = len(sources)

        market_score = trend.get("market_score", 0)
        competition_score = trend.get("competition_score", 0)
        velocity_score = trend.get("velocity_score", 0)
        google_validation_score = trend.get("google_validation_score", 0)
        source_diversity_score = trend.get("source_diversity_score", 0)
        engagement_score = trend.get("engagement_score", 0)
        time_to_mainstream = trend.get("time_to_mainstream", "Unknown")

        idea = choose_positioning(trend)

        why_it_matters = make_why_it_matters(
            keyword,
            signals,
            source_count,
            trend_score,
            velocity_score
        )

        risk_note = make_risk_note(
            competition_score,
            source_count,
            trend_score
        )

        founder_action = make_founder_action(
            keyword,
            idea["action"],
            source_count,
            market_score
        )

        # simple opportunity type label
        if market_score >= 0.8 and competition_score >= 0.6:
            opportunity_type = "D2C product"
        elif source_count >= 3:
            opportunity_type = "content-led brand"
        elif trend_score < 0.5:
            opportunity_type = "watchlist trend"
        else:
            opportunity_type = "niche wellness opportunity"

        opportunity = {
            "trend": keyword,
            "trend_score": trend_score,
            "signals": signals,
            "sources": sources,
            "market_score": market_score,
            "competition_score": competition_score,
            "velocity_score": velocity_score,
            "google_validation_score": google_validation_score,
            "source_diversity_score": source_diversity_score,
            "engagement_score": engagement_score,
            "time_to_mainstream": time_to_mainstream,
            "opportunity_type": opportunity_type,
            "opportunity_brief": {
                "why_it_matters": why_it_matters,
                "evidence": {
                    "signals_detected": signals,
                    "source_count": source_count,
                    "sources": sources,
                    "trend_score": trend_score,
                    "velocity_score": velocity_score,
                    "market_score": market_score,
                    "competition_score": competition_score,
                    "google_validation_score": google_validation_score,
                    "source_diversity_score": source_diversity_score,
                    "engagement_score": engagement_score,
                    "time_to_mainstream": time_to_mainstream
                },
                "product_recommendation": f"Consider building {idea['product']}.",
                "category_recommendation": f"Potential category: {idea['category']}.",
                "risk_note": risk_note,
                "founder_action": founder_action
            }
        }

        opportunities.append(opportunity)

    os.makedirs("data", exist_ok=True)

    with open("data/startup_opportunities.json", "w", encoding="utf-8") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    print(f"{len(opportunities)} startup opportunities generated.")
    print("Saved to data/startup_opportunities.json")

    return opportunities
