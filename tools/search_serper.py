import os
import httpx

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def serper_search(query:str, k: int=1):

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": k}

    with httpx.Client(timeout=20) as client:
        r = client.post(url, headers=headers,json=payload)
        r.raise_for_status()
        data = r.json()

    results = data.get("organic", [])
    out = []
    for item in results[:k]:
        out.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return out
