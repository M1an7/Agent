import httpx

# Fetch the HTML content of a given URL
def fetch_html(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (ResearchAgent/1.0)"}
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            r = client.get(url, headers=headers)
            if r.status_code != 200:
                return None
            return r.text
    except Exception as e:
        return None
