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


def fetch_pubmed_signals():
    signals = []

    for term in PUBMED_TERMS:
        try:
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                f"?db=pubmed&term={term.replace(' ', '+')}&retmax=5&sort=date"
            )
            search_response = requests.get(search_url, timeout=15)
            search_response.raise_for_status()

            root = ET.fromstring(search_response.content)
            ids = [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]

            if not ids:
                continue

            for pubmed_id in ids:
                signals.append({
                    "source": "pubmed",
                    "keyword": term.lower(),
                    "title": f"Recent PubMed signal for {term}",
                    "description": f"PubMed ID: {pubmed_id}",
                    "score": 40,
                    "category": "research"
                })

        except Exception:
            continue

    return signals