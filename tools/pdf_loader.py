from __future__ import annotations
from dataclasses import dataclass
from typing import List
import fitz

@dataclass
class PageDoc:
    page: int
    text: str

def load_pdf_pages(pdf_path:str)->List[PageDoc]:
    with fitz.open(pdf_path) as doc:
        pages: List[PageDoc]=[]
        for i in range(doc.page_count):
            page = doc.load_page(i)
            text = (page.get_text("text") or "").strip()
            if text:
                pages.append(PageDoc(page=i+1, text=text))
        return pages