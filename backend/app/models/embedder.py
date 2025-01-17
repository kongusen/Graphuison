from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import torch

class SentenceEmbedder:
    def __init__(self, model_name='moka-ai/m3e-base', device="cpu"):
        self.device = device
        self._model = None
        self.model_name = model_name

    def _load_model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)

    def embed_sentences(self, sentences: List[str]) -> np.ndarray:
        self._load_model()
        embeddings = self._model.encode(sentences, convert_to_tensor=True)
        return embeddings.cpu().numpy()