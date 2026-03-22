from __future__ import annotations
import os
from typing import Any, Dict, List, Tuple
import numpy as np
import faiss
import pickle

class FaissStore:
    def __init__(self, dim:int, index_dir: str):
        self.dim = dim
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

        self.index_path = os.path.join(index_dir,"index.faiss")
        self.meta_path = os.path.join(index_dir,"metas.pkl")
        self.texts_path = os.path.join(index_dir,"texts.pkl")

        self.index = faiss.IndexFlatIP(dim)
        self.metas:List[Dict[str, Any]] = []
        self.texts:List[str] = []

    @staticmethod
    def _normalize(v:np.ndarray)->np.ndarray:
        faiss.normalize_L2(v)
        return v
    
    def add(self, vectors: np.ndarray, texts: List[str], metas: List[Dict[str, Any]]):
        vectors = vectors.astype(np.float32)
        vectors = self._normalize(vectors)
        self.index.add(vectors)
        self.texts.extend(texts)
        self.metas.extend(metas)

    def search(self, query_vec:np.ndarray, top_k: int=5) -> List[Tuple[float, str, Dict[str, Any]]]:
        q = query_vec.reshape(1,-1).astype(np.float32)
        q = self._normalize(q)
        scores, idx = self.index.search(q, top_k)
        out = []
        for s, i in zip(scores[0],idx[0]):
            if i == -1:
                continue
            out.append((float(s), self.texts[i], self.metas[i]))
        return out
    
    def save(self):
        faiss.write_index(self.index, self.index_path)
        input("debuging")
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metas, f)
        with open(self.texts_path, "wb") as f:
            pickle.dump(self.texts,f)

    @classmethod
    def load(cls, index_dir:str) -> "FaissStore":
        index_path = os.path.join(index_dir,"index.faiss")
        meta_path = os.path.join(index_dir,"metas.pkl")
        texts_path = os.path.join(index_dir,"texts.pkl")

        index = faiss.read_index(index_path)
        store = cls(dim=index.d, index_dir=index_dir)
        store.index = index
        with open(meta_path,"rb") as f:
            store.metas = pickle.load(f)
        with open(texts_path,"rb") as f:
            store.texts = pickle.load(f)
        return store