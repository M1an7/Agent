from tools.embedder import Embedder
from tools.pdf_loader import load_pdf_pages
from tools.faiss_store import FaissStore
from utils.chunker import chunk_pages
from agent.prompts import RAG_QA_PROMPT
import os 
from openai import OpenAI
from tqdm import tqdm
from typing import List

class RagAgent:
    def __init__(self):
        self.index_dir = os.getenv("RAG_INDEX_DIR", "mvp/data/index")
        self.top_k = int(os.getenv("RAG_TOP_K", "5"))
        self.chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
        self.chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))

        self.embedder = Embedder()
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE_URL","").strip() or None
        self.llm_model = os.getenv("LLM_MODEL","sherry_server")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    
    def ingest_pdf(self, pdf_path:str):

        print("CWD =", os.getcwd())
        print("INDEX_DIR(abs) =", os.path.abspath(self.index_dir))

        os.makedirs("data/docs", exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)

        source_name = os.path.basename(pdf_path)   # 提取文件名（含扩展名）
        pages = load_pdf_pages(pdf_path)
        page_tuples = [(p.page, p.text) for p in pages]
        chunks = chunk_pages(
            page_tuples,
            source_name=source_name,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        if not chunks:
            raise RuntimeError("No text extracted from PDF. It may be scanned, OCR is needed.")
        
        texts = [c.text for c in chunks]
        metas = [c.meta for c in chunks]

        probe = self.embedder.embed_query("dimension probe")    # 探针用于探测嵌入模型的向量维度,即下文的dim
        store = FaissStore(dim=probe.shape[0], index_dir=self.index_dir)

        batch = 16
        for i in tqdm(range(0,len(texts),batch),desc = "Embedding..."):
            vecs = self.embedder.embed_texts(texts[i:i+batch])
            store.add(vecs, texts[i:i+batch], metas[i:i+batch])

        store.save()
        return f"Indexed {len(texts)} chunks -> {self.index_dir}"
    
    def ask(self, question:str) -> str:
        store = FaissStore.load(self.index_dir)
        qvec = self.embedder.embed_query(question)
        hits = store.search(qvec, top_k=self.top_k)

        context = self._format_context(hits, max_char=8000)
        prompt = RAG_QA_PROMPT.format(question=question, context=context)

        resp = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content

    #从向量数据库中检索到的相关内容，合成上下文依据
    def _format_context(self, hits, max_char=8000) -> str:
        blocks:List[str]=[]
        used = 0
        for score, text, meta in hits:
            src = meta.get("source","unknown")
            ps, pe = meta.get("page_start","?"), meta.get("page_end","?")
            header = f"[Context] score={score:.3f} source={src} p.{ps}-{pe}\n"
            block = header + text.strip() + "\n\n"
            if used + len(block) > max_char:
                break
            blocks.append(block)
            used += len(block)
        return "".join(blocks).strip()