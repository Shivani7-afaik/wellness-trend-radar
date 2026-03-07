import requests
import xml.etree.ElementTree as ET

PUBMED_TERMS = [
    "creatine cognition",
    "magnesium glycinate sleep",
    "ashwagandha stress",
    "collagen peptides skin",
    "lion's mane cognition",
    "electrolytes hydration",
    "gut microbiome supplement",
    "sleep gummies melatonin",
    "sea moss supplement",
    "colostrum immunity",
    "mushroom coffee",
    "cordyceps exercise",
    "berberine metabolism",
    "probiotic drinks gut health"
]


def clean_pubmed_keyword(term):
    term = term.lower()
    replacements = [
        " cognition",
        " sleep",
        " stress",
        " skin",
        " hydration",
        " supplement",
        " immunity",
        " exercise",
        " metabolism",
        " melatonin",
    ]
    for r in replacements:
        term = term.replace(r, "")
    return term.strip()


def fetch_pubmed_signals():
    signals = []

    for term in PUBMED_TERMS:
        try:
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                f"?db=pubmed&term={term.replace(' ', '+')}&retmax=20&sort=date"
            )
            search_response = requests.get(search_url, timeout=15)
            search_response.raise_for_status()

            root = ET.fromstring(search_response.content)
            ids = [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]

            paper_count = len(ids)

            if paper_count == 0:
                continue

            keyword = clean_pubmed_keyword(term)

            signals.append({
                "source": "pubmed",
                "keyword": keyword,
                "title": f"Recent PubMed research signal for {term}",
                "description": f"{paper_count} recent PubMed papers found",
                "score": min(100, paper_count * 5),
                "category": "research",
                "paper_count": paper_count
            })

        except Exception:
            continue

    return signals
