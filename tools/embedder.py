import os
from openai import OpenAI
from typing import List
import numpy as np
class Embedder:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_EMBED_URL", "").strip() or None
        self.model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def embed_texts(self,texts:List[str])->np.ndarray:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
        return vecs
    
    def embed_query(self, text:str) ->np.ndarray:
        return self.embed_texts([text])[0]
        