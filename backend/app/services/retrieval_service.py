from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.core.config import settings

class RetrievalService:
    @staticmethod
    def retrieve_context_for_queries(
        role_id: str,
        queries: List[str],
        top_k: int = settings.RETRIEVAL_TOP_K,
        similarity_threshold: float = settings.SIMILARITY_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Retrieves grounded, role-filtered textbook chunks across multiple focused semantic queries.
        Deduplicates chunks based on chunk_id and preserves source page citations.
        """
        all_retrieved_map: Dict[str, Dict[str, Any]] = {}
        valid_queries = [q.strip() for q in queries if q.strip()]
        if not valid_queries:
            return []

        # Batch embed all queries simultaneously for 4x faster retrieval
        query_embeddings = embedding_service.embed_batch(valid_queries)

        for query, query_embedding in zip(valid_queries, query_embeddings):
            results = vector_store.query(
                role_id=role_id,
                query_embedding=query_embedding,
                top_k=top_k
            )

            for item in results:
                cid = item["chunk_id"]
                sim = item.get("similarity", 0.0)
                
                # Filter by similarity threshold to avoid irrelevant noise
                if sim < similarity_threshold:
                    continue

                if cid not in all_retrieved_map:
                    item["matched_queries"] = [query]
                    all_retrieved_map[cid] = item
                else:
                    all_retrieved_map[cid]["matched_queries"].append(query)
                    # Keep the highest similarity score
                    if sim > all_retrieved_map[cid]["similarity"]:
                        all_retrieved_map[cid]["similarity"] = sim

        # Sort by similarity descending
        sorted_results = sorted(
            all_retrieved_map.values(),
            key=lambda x: x.get("similarity", 0.0),
            reverse=True
        )

        return sorted_results

retrieval_service = RetrievalService()

