import os
from datetime import datetime


def safe(val, default=""):
    return val if val is not None else default


def fmt_score(value):
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "0.00"


def make_source_badges(sources):
    if not sources:
        return "<span class='badge'>No source</span>"

    badges = []
    for source in sources:
        badges.append(f"<span class='badge'>{source}</span>")
    return " ".join(badges)


def generate_report(opportunities):
    os.makedirs("data", exist_ok=True)

    total_trends = len(opportunities)
    avg_score = (
        sum(float(o.get("trend_score", 0) or 0) for o in opportunities) / total_trends
        if total_trends > 0 else 0
    )

    strongest_sources = {}
    for opp in opportunities:
        for source in opp.get("sources", []):
            strongest_sources[source] = strongest_sources.get(source, 0) + 1

    top_sources_sorted = sorted(
        strongest_sources.items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_sources_text = ", ".join([f"{name} ({count})" for name, count in top_sources_sorted[:5]])
    if not top_sources_text:
        top_sources_text = "No sources available"

    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Wellness Trend Radar</title>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, Helvetica, sans-serif;
                background: #f6f8fb;
                color: #1f2937;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 32px 20px 60px;
            }}

            .hero {{
                background: linear-gradient(135deg, #0f172a, #1e293b 55%, #0ea5a4);
                color: white;
                padding: 36px;
                border-radius: 20px;
                margin-bottom: 28px;
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
            }}

            .hero h1 {{
                margin: 0 0 10px;
                font-size: 34px;
                line-height: 1.2;
            }}

            .hero p {{
                margin: 6px 0;
                font-size: 15px;
                color: rgba(255,255,255,0.9);
            }}

            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
                margin: 24px 0 34px;
            }}

            .summary-card {{
                background: white;
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
                border: 1px solid #e5e7eb;
            }}

            .summary-label {{
                font-size: 13px;
                color: #6b7280;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }}

            .summary-value {{
                font-size: 28px;
                font-weight: 700;
                color: #111827;
            }}

            .summary-sub {{
                margin-top: 8px;
                font-size: 13px;
                color: #6b7280;
            }}

            .section-title {{
                font-size: 24px;
                font-weight: 700;
                margin: 10px 0 18px;
                color: #111827;
            }}

            .trend-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 20px;
            }}

            .trend-card {{
                background: white;
                border-radius: 18px;
                padding: 22px;
                box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
                border: 1px solid #e5e7eb;
                position: relative;
            }}

            .rank {{
                position: absolute;
                top: 16px;
                right: 16px;
                background: #111827;
                color: white;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 10px;
                border-radius: 999px;
            }}

            .trend-title {{
                margin: 0 0 12px;
                font-size: 24px;
                color: #0f172a;
                text-transform: capitalize;
                padding-right: 70px;
            }}

            .score-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 16px;
            }}

            .score-pill {{
                display: inline-block;
                background: #dcfce7;
                color: #166534;
                border-radius: 999px;
                padding: 8px 14px;
                font-weight: 700;
                font-size: 14px;
            }}

            .opportunity-type {{
                display: inline-block;
                background: #e0f2fe;
                color: #075985;
                border-radius: 999px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 700;
            }}

            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 10px;
                margin: 18px 0;
            }}

            .metric {{
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px;
            }}

            .metric .label {{
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 6px;
            }}

            .metric .value {{
                font-size: 18px;
                font-weight: 700;
                color: #111827;
            }}

            .subsection {{
                margin-top: 16px;
                padding-top: 14px;
                border-top: 1px solid #eef2f7;
            }}

            .subsection h3 {{
                margin: 0 0 10px;
                font-size: 15px;
                color: #0f172a;
            }}

            .subsection p {{
                margin: 0;
                font-size: 14px;
                line-height: 1.6;
                color: #374151;
            }}

            .badge-row {{
                margin-top: 10px;
            }}

            .badge {{
                display: inline-block;
                margin: 0 8px 8px 0;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 700;
                border-radius: 999px;
                background: #f1f5f9;
                color: #334155;
                border: 1px solid #dbeafe;
            }}

            .evidence-list {{
                margin: 0;
                padding-left: 18px;
                color: #374151;
                font-size: 14px;
                line-height: 1.7;
            }}

            .footer {{
                margin-top: 36px;
                padding: 18px 0 0;
                color: #6b7280;
                font-size: 13px;
                border-top: 1px solid #e5e7eb;
            }}

            @media (max-width: 700px) {{
                .trend-title {{
                    font-size: 20px;
                }}

                .hero h1 {{
                    font-size: 28px;
                }}

                .metric-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>Wellness Trend Radar</h1>
                <p>AI-powered scan of emerging wellness signals across digital platforms and research sources.</p>
                <p><strong>Region:</strong> India</p>
                <p><strong>Generated:</strong> {generated_at}</p>
            </div>

            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-label">Top Trends Identified</div>
                    <div class="summary-value">{total_trends}</div>
                    <div class="summary-sub">Highest-potential trends selected for this report</div>
                </div>

                <div class="summary-card">
                    <div class="summary-label">Average Trend Score</div>
                    <div class="summary-value">{fmt_score(avg_score)}</div>
                    <div class="summary-sub">Average signal strength across shortlisted trends</div>
                </div>

                <div class="summary-card">
                    <div class="summary-label">Top Data Sources</div>
                    <div class="summary-value" style="font-size:18px;">{top_sources_text}</div>
                    <div class="summary-sub">Most frequent sources contributing to the report</div>
                </div>
            </div>

            <div class="section-title">Top Emerging Wellness Opportunities</div>
            <div class="trend-grid">
    """

    for idx, t in enumerate(opportunities, start=1):
        trend = safe(t.get("trend"), "Unknown Trend")
        trend_score = fmt_score(t.get("trend_score", 0))
        signals = safe(t.get("signals"), 0)
        sources = t.get("sources", [])
        opportunity_type = safe(t.get("opportunity_type"), "Wellness Opportunity")
        market_score = fmt_score(t.get("market_score", 0))
        competition_score = fmt_score(t.get("competition_score", 0))
        velocity_score = fmt_score(t.get("velocity_score", 0))
        google_validation_score = fmt_score(t.get("google_validation_score", 0))
        source_diversity_score = fmt_score(t.get("source_diversity_score", 0))
        engagement_score = fmt_score(t.get("engagement_score", 0))
        time_to_mainstream = safe(t.get("time_to_mainstream"), "Unknown")

        brief = t.get("opportunity_brief", {})
        why_it_matters = safe(brief.get("why_it_matters"), "No summary available.")
        product_recommendation = safe(brief.get("product_recommendation"), "No recommendation available.")
        category_recommendation = safe(brief.get("category_recommendation"), "No category recommendation available.")
        risk_note = safe(brief.get("risk_note"), "No major risk note available.")
        founder_action = safe(brief.get("founder_action"), "No founder action available.")

        html += f"""
                <div class="trend-card">
                    <div class="rank">#{idx}</div>
                    <h2 class="trend-title">{trend}</h2>

                    <div class="score-row">
                        <span class="score-pill">Trend Score: {trend_score}</span>
                        <span class="opportunity-type">{opportunity_type}</span>
                    </div>

                    <div class="badge-row">
                        {make_source_badges(sources)}
                    </div>

                    <div class="metric-grid">
                        <div class="metric">
                            <div class="label">Signals Detected</div>
                            <div class="value">{signals}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Time to Mainstream</div>
                            <div class="value">{time_to_mainstream}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Velocity Score</div>
                            <div class="value">{velocity_score}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Market Score</div>
                            <div class="value">{market_score}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Competition Score</div>
                            <div class="value">{competition_score}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Google Validation</div>
                            <div class="value">{google_validation_score}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Source Diversity</div>
                            <div class="value">{source_diversity_score}</div>
                        </div>
                        <div class="metric">
                            <div class="label">Engagement Score</div>
                            <div class="value">{engagement_score}</div>
                        </div>
                    </div>

                    <div class="subsection">
                        <h3>Why it matters</h3>
                        <p>{why_it_matters}</p>
                    </div>

                    <div class="subsection">
                        <h3>Opportunity recommendation</h3>
                        <p>{product_recommendation}</p>
                    </div>

                    <div class="subsection">
                        <h3>Category recommendation</h3>
                        <p>{category_recommendation}</p>
                    </div>

                    <div class="subsection">
                        <h3>Risk note</h3>
                        <p>{risk_note}</p>
                    </div>

                    <div class="subsection">
                        <h3>Founder action</h3>
                        <p>{founder_action}</p>
                    </div>

                    <div class="subsection">
                        <h3>Evidence snapshot</h3>
                        <ul class="evidence-list">
                            <li><strong>Source count:</strong> {len(sources)}</li>
                            <li><strong>Sources:</strong> {", ".join(sources) if sources else "None"}</li>
                            <li><strong>Signals detected:</strong> {signals}</li>
                            <li><strong>Trend score:</strong> {trend_score}</li>
                        </ul>
                    </div>
                </div>
        """

    html += """
            </div>

            <div class="footer">
                This report was automatically generated by Wellness Trend Radar. The output is intended for exploration,
                opportunity scanning, and founder validation rather than medical or financial decision-making.
            </div>
        </div>
    </body>
    </html>
    """

    with open("trend_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Trend report generated: trend_report.html")
