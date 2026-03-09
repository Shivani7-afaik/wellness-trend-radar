Here is the updated README with all emojis removed.

---

# Wellness Trend Radar (India 2026)

An AI-powered market intelligence engine that detects emerging health and wellness white-spaces in the Indian market. By triangulating social momentum (Reddit, YouTube, Google Trends) with clinical validation (PubMed Central), the Radar identifies high-potential startup opportunities before they hit the mainstream.

## Key Features

* **Multi-Channel Signal Synthesis**: Scrapes and aggregates data from Reddit communities, YouTube velocity, and Google Search intent.
* **PubMed Clinical Validation**: Automatically cross-references discovered trends with the National Library of Medicine to calculate Science Scores.
* **Top 15 Intelligence**: Focuses exclusively on the top 15 highest-scoring trends to prevent data fatigue.
* **Founder Action Plans**: Generates dynamic "Why it Matters" and "Founder Strategy" briefs for every identified trend.
* **High-Contrast Dashboard**: A sleek, command-center style Streamlit UI optimized for clarity and decision-making.

## Tech Stack

* **Frontend**: Streamlit (with custom CSS injection)
* **Analysis**: Pandas, NumPy
* **Scraping/APIs**: Requests, PubMed E-Utilities, Google Trends
* **Logic**: Dynamic Opportunity Generator with Weighted Intensity Scoring

## Scoring Logic

The "Trend Intensity" score is calculated using a proprietary formula:

$$Score = 0.3 + (UniqueSources \times 0.15) + (PubMedPapers \times 0.001)$$

* **Base (0.3)**: Initial discovery signal.
* **Source Diversity (Max 0.45)**: Rewarded for appearing across multiple platforms (e.g., Reddit + YouTube).
* **Clinical Weight (Max 0.25)**: Rewarded for a deep body of existing research papers.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/wellness-trend-radar.git
cd wellness-trend-radar

```


2. **Install dependencies**:
```bash
pip install -r requirements.txt

```


3. **Run the Dashboard**:
```bash
streamlit run streamlit_app.py

```



## Project Structure

* `streamlit_app.py`: The main UI and dashboard controller.
* `trend_scraper.py`: Handles social media and search engine data collection.
* `research_scraper.py`: Interfaces with PubMed to fetch paper counts.
* `opportunity_generator.py`: Converts raw data into business strategy briefs.
* `data/`: Stores JSON snapshots of the latest market scans.

## Disclaimer

This tool is for market research and startup exploration purposes only. Trend data is based on digital signals and should not be taken as medical or investment advice.

---

*Built for the next generation of Indian Wellness Founders.*
