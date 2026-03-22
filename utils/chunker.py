from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Chunk:
    chunk_id:str
    text:str
    meta: Dict[str,Any]

#将页按一定字符数分块，每块之间有overlap个字符重叠，输入pages，输出chunks
def chunk_pages(
        pages:List[Tuple[int, str]],
        source_name:str,
        chunk_size: int = 1200,
        overlap: int = 200,
) -> List[Chunk]:
    chunks:List[Chunk] = []
    buf = ""
    page_start = None
    page_end = None
    idx = 0


    def flush():
        nonlocal idx, buf, page_start, page_end
        if buf.strip():
            chunks.append(
                Chunk(
                    chunk_id=f"{source_name}::chunk_{idx}",
                    text=buf.strip(),
                    meta={
                        "source": source_name,
                        "page_start": page_start, 
                        "page_end": page_end,
                    },
                )
            )
            idx += 1


    for pno, text in pages:
        if page_start is None:
            page_start = pno
        page_end = pno

        if len(buf) + len(text) +1 <= chunk_size:
            buf = buf + "\n" + text if buf else text
        else:
            flush()

            if overlap>0 and len(buf) > overlap:
                buf = buf[-overlap:]
            else:
                buf = ""
            page_start = pno
            page_end = pno
            buf = buf + "\n" + text if buf else text
    
    flush()
    return chunks