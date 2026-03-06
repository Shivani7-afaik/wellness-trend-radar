import json

def generate_report(opportunities):

    html = """
    <html>
    <head>
        <title>Wellness Trend Radar</title>
        <style>
            body {font-family: Arial; margin:40px;}
            h1 {color:#333;}
            .trend {border:1px solid #ddd; padding:20px; margin-bottom:20px; border-radius:8px;}
            .score {font-weight:bold; color:#2c7;}
        </style>
    </head>
    <body>
    <h1>Emerging Wellness Trends (India)</h1>
    """

    for t in opportunities:

        html += f"""
        <div class="trend">
        <h2>{t['trend']}</h2>
        <p class="score">Trend Score: {t['trend_score']}</p>
        <p><b>Signals:</b> {t['signals']}</p>
        <p><b>Sources:</b> {', '.join(t['sources'])}</p>
        <p><b>Why it matters:</b> {t['opportunity_brief']['why_it_matters']}</p>
        <p><b>Opportunity:</b> {t['opportunity_brief']['product_recommendation']}</p>
        </div>
        """

    html += "</body></html>"

    with open("trend_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Trend report generated: trend_report.html")