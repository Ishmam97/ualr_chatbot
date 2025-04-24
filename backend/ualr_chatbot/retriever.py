import pickle
import numpy as np
import os
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false" 
from sentence_transformers import SentenceTransformer
import faiss

class Retriever:
    def __init__(self, index_path, metadata_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.doc_metadata = pickle.load(f)

    def query(self, text, k=3):
        embedding = self.model.encode([text], normalize_embeddings=True)
        D, I = self.index.search(np.array(embedding), k)
        return [self.doc_metadata[i] for i in I[0]]
