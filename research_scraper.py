import requests
import xml.etree.ElementTree as ET

try:
    import certifi
    _certifi_available = True
except ImportError:
    _certifi_available = False


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


def make_request(url, params=None, timeout=20):
    headers = {
        "User-Agent": "WellnessTrendRadar/1.0 (research scraper)"
    }

    request_kwargs = {
        "headers": headers,
        "params": params,
        "timeout": timeout,
    }

    if _certifi_available:
        request_kwargs["verify"] = certifi.where()

    return requests.get(url, **request_kwargs)


def fetch_pubmed_signals():
    signals = []

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    for term in PUBMED_TERMS:
        try:
            params = {
                "db": "pubmed",
                "term": term,
                "retmax": 20,
                "sort": "date",
                "retmode": "xml"
            }

            search_response = make_request(base_url, params=params, timeout=20)
            search_response.raise_for_status()

            root = ET.fromstring(search_response.content)
            ids = [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]

            paper_count = len(ids)

            if paper_count == 0:
                print(f"PubMed: 0 papers for '{term}'")
                continue

            keyword = clean_pubmed_keyword(term)

            signals.append({
                "source": "pubmed",
                "keyword": keyword,
                "title": f"Recent PubMed research signal for {term}",
                "description": f"{paper_count} recent PubMed papers found",
                "score": min(100, paper_count * 5),
                "category": "research",
                "paper_count": paper_count,
                "date": "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={term.replace(' ', '+')}"
            })

            print(f"PubMed: {paper_count} papers for '{term}'")

        except requests.exceptions.SSLError as e:
            print(f"PubMed SSL error for '{term}': {e}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"PubMed request failed for '{term}': {e}")
            continue
        except ET.ParseError as e:
            print(f"PubMed XML parse failed for '{term}': {e}")
            continue
        except Exception as e:
            print(f"PubMed unexpected error for '{term}': {e}")
            continue

    return signals
