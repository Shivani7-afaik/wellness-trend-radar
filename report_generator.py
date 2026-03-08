import os
from datetime import datetime

def generate_report(opportunities):
    os.makedirs("data", exist_ok=True)
    
    # FETCH REAL TIME (India Standard Time)
    now = datetime.now()
    generated_at = now.strftime("%d %b %Y, %I:%M %p")
    
    # Calculate Summary Stats
    total_trends = len(opportunities)
    avg_intensity = sum(o.get('trend_score', 0) for o in opportunities) / total_trends if total_trends > 0 else 0
    
    source_counts = {}
    for o in opportunities:
        for s in o.get('sources', []):
            source_counts[s] = source_counts.get(s, 0) + 1
    channels_text = ", ".join([f"{name} ({count})" for name, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:4]])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #f8fafc; padding: 40px; color: #1e293b; }}
            .hero {{ background: #0f172a; color: white; padding: 35px; border-radius: 12px; margin-bottom: 30px; }}
            .header-stats {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 40px; }}
            .stat-card {{ background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; }}
            .stat-label {{ font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; }}
            .stat-val {{ font-size: 22px; font-weight: 800; margin-top: 10px; color: #0f172a; }}
            
            .trend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; }}
            .trend-card {{ background: white; border-radius: 16px; padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
            
            .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }}
            .m-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; }}
            .source-highlight {{ border-color: #3b82f6; background: #eff6ff; }}
            .m-label {{ font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 700; }}
            .m-val {{ font-size: 15px; font-weight: 700; margin-top: 5px; }}
            
            .section-header {{ font-size: 12px; font-weight: 800; color: #475569; text-transform: uppercase; margin-top: 25px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; }}
            .content-text {{ font-size: 14px; line-height: 1.6; color: #334155; margin-top: 12px; }}
        </style>
    </head>
    <body>
        <div class="hero">
            <h1 style="margin:0; font-size: 32px;">Wellness Trend Radar</h1>
            <p style="opacity:0.8; font-size: 14px; margin-top: 10px;">Region: India | Generated: {generated_at}</p>
        </div>

        <div class="header-stats">
            <div class="stat-card"><div class="stat-label">Active Trends</div><div class="stat-val">{total_trends} High-Potential</div></div>
            <div class="stat-card"><div class="stat-label">Avg. Market Intensity</div><div class="stat-val">{avg_intensity:.2f} / 1.0</div></div>
            <div class="stat-card"><div class="stat-label">Primary Channels</div><div class="stat-val" style="font-size:13px; line-height:1.4;">{channels_text}</div></div>
        </div>

        <div class="trend-grid">
    """

    for idx, opp in enumerate(opportunities, start=1):
        brief = opp.get("opportunity_brief", {})
        primary = opp.get('sources', ['N/A'])[0].upper()
        
        html += f"""
        <div class="trend-card">
            <a href="{opp['trend_link']}" target="_blank" style="text-decoration:none; color:#0f172a;"><h2 style="margin:0; font-size:26px;">{opp['trend']} 🔗</h2></a>
            
            <div class="metric-grid">
                <div class="m-box"><div class="m-label">Time to Mainstream</div><div class="m-val">6-12 Months</div></div>
                <div class="m-box"><div class="m-label">Market Size Score</div><div class="m-val">{opp['trend_score']}</div></div>
                <div class="m-box"><div class="m-label">Research Signals</div><div class="m-val">{opp['pubmed_papers']} Papers</div></div>
                <div class="m-box source-highlight"><div class="m-label" style="color:#3b82f6;">Primary Source</div><div class="m-val" style="color:#1d4ed8;">{primary}</div></div>
            </div>

            <div class="section-header">Strategy: Why It Matters</div>
            <p class="content-text">{brief.get('why_it_matters')}</p>

            <div class="section-header" style="color:#0f172a;">Subjective Founder Action</div>
            <p class="content-text" style="font-weight:500; background:#f0f9ff; padding:20px; border-radius:10px; border-left:5px solid #3b82f6;">{brief.get('founder_action')}</p>
        </div>
        """

    html += "</div></body></html>"
    with open("trend_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    return True
