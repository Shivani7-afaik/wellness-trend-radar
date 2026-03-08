import requests
import time
import re

def fetch_pubmed_signals(keyword):
    """Returns the total number of papers for a keyword as an integer."""
    # Using a simpler URL structure for broad searches
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={keyword}&rettype=count"
    
    try:
        response = requests.get(url, timeout=10)
        # Use Regex to find the number between <Count> tags - very robust
        match = re.search(r'<Count>(\d+)</Count>', response.text)
        
        if match:
            count = int(match.group(1))
            print(f"PubMed: Found {count} for {keyword}")
            return count
        return 0
    except Exception as e:
        print(f"PubMed connection error: {e}")
        return 0
    finally:
        time.sleep(0.3)
