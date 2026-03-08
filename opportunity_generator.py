def generate_opportunities(trends):
    opportunities = []

    for t in trends:
        kw_raw = t.get("keyword", "Unknown")
        kw_cap = kw_raw.title()
        sources = t.get("sources", [])
        pubmed = t.get("pubmed_papers", 0)
        
        # --- DYNAMIC SCORING LOGIC ---
        # Base (0.4) + 0.15 per source + normalized research weight
        source_weight = len(sources) * 0.15
        # Higher paper counts add significantly to the score
        research_weight = min(pubmed * 0.01, 0.3) 
        dynamic_score = min(0.4 + source_weight + research_weight, 1.0)
        
        # Dynamic search link
        search_link = f"https://www.google.com/search?q={kw_raw.replace(' ', '+')}+market+india"

        # --- DYNAMIC WRITE-UPS ---
        if "collagen" in kw_raw.lower():
            why = f"{kw_cap} is shifting from a beauty luxury to a longevity essential as Indian consumers seek ingestible skin-health solutions."
            action = f"To win in the {kw_cap} space, move away from generic tubs. Launch a high-potency {kw_cap} liquid shot with added Vitamin C for absorption. Target the 35+ urban demographic on Instagram by focusing on Visible Skin Density and Joint Lubrication rather than just Anti-Aging. Your founder move is to bundle it as a 30-day subscription to ensure high LTV."
        
        elif "creatine" in kw_raw.lower():
            why = f"{kw_cap} is breaking out of the bodybuilding niche and being adopted by the Biohacking community for its cognitive benefits."
            action = f"Position {kw_cap} as Fuel for the Modern Brain. Launch a flavorless, high-solubility {kw_cap} powder designed to be mixed into morning coffee or tea without clumping. Market it to the Bangalore/Mumbai tech scene as a tool for Mental Endurance and End-of-Day Clarity. Avoid muscle imagery; use clean, minimalist laboratory-style packaging."
        
        elif "ashwagandha" in kw_raw.lower():
            why = f"{kw_cap} is the anchor of the Indian Stress-Stack, moving into sophisticated delivery formats like gummies and transdermal patches."
            action = f"Differentiate your {kw_cap} by focusing on Standardized Potency. Launch a PM-Recovery gummy that combines KSM-66 {kw_cap} with Magnesium for sleep architecture. Your founder move is to include a Stress-Tracker journal with every order, encouraging users to log their cortisol-related symptoms to build long-term brand loyalty through results."
        
        else:
            # Fallback that still uses specific counts and keyword name
            why = f"{kw_cap} is gaining significant traction across {len(sources)} digital signals, suggesting a gap between current supply and emerging Indian consumer intent."
            action = f"The core opportunity for {kw_cap} lies in Format Innovation. Rather than a standard pill, develop a {kw_cap} sublingual strip or an effervescent tablet to solve for pill-fatigue. Use your {pubmed} research citations to build a Science-First landing page and run a pre-order campaign specifically for early adopters in the biohacking space."

        opportunities.append({
            "trend": kw_cap,
            "trend_link": search_link,
            "sources": sources,
            "pubmed_papers": pubmed, 
            "trend_score": round(dynamic_score, 2),
            "opportunity_brief": {
                "why_it_matters": why,
                "founder_action": action,
                "time_to_mainstream": "6-12 months"
            }
        })
    return opportunities
