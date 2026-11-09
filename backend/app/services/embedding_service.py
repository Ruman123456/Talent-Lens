from typing import List, Optional
import os
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            # Load sentence transformer model
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = self._get_model()
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

# Global singleton
embedding_service = EmbeddingService()

