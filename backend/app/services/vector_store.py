import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import os
from app.core.config import settings

class ChromaVectorStore:
    def __init__(self, persist_directory: str = settings.CHROMA_PERSIST_DIRECTORY):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def get_or_create_collection(self, role_id: str):
        collection_name = f"role_{role_id}"
        # Chroma collection names must be 3-63 characters, alphanumeric, underscores or hyphens
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"role": role_id}
        )

    def add_chunks(
        self,
        role_id: str,
        chunk_ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        collection = self.get_or_create_collection(role_id)
        collection.upsert(
            ids=chunk_ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def query(
        self,
        role_id: str,
        query_embedding: List[float],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(role_id)
        count = collection.count()
        if count == 0:
            return []
        
        n_results = min(top_k, count)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc_text, meta, dist, cid in zip(docs, metas, distances, ids):
                # distance to similarity approximation
                retrieved.append({
                    "chunk_id": cid,
                    "text": doc_text,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": round(1.0 / (1.0 + float(dist)), 4)
                })
        return retrieved

    def get_role_stats(self, role_id: str) -> Dict[str, Any]:
        collection = self.get_or_create_collection(role_id)
        return {
            "total_chunks": collection.count()
        }

vector_store = ChromaVectorStore()

