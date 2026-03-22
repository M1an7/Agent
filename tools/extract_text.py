from readability import Document
from bs4 import BeautifulSoup

def extract_main_text(html:str) -> str:
    try:
        doc = Document(html)
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, "lxml")
        text = soup.get_text(separator="\n")
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    except Exception:
        return ""