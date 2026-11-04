"""
Semantic similarity retrieval - embeds incoming text with a sentence-
transformer and searches a persistent ChromaDB collection of pre-indexed
financial articles for the closest matches by meaning (not keyword overlap).

Two-part lazy loading, same pattern as sentiment/credibility services:
- the embedding model loads once, cached
- the Chroma collection connects once, cached

chromadb and sentence-transformers are imported inside _ensure_loaded, so importing this
module (for example in unit tests) does not need them.

Self-matches: if the claim is already an indexed headline, that article is the best
possible evidence, so the product KEEPS it. Benchmarks that must not count a query
retrieving itself pass exclude_self=True.
"""
import os
import re
import threading

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.retrieval import SimilarArticleResult, SimilarArticlesResponse

logger = get_logger(__name__)

NEAR_DUPLICATE_THRESHOLD = 0.97  # only used when exclude_self=True; not tuned on data


def _normalize(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


class RetrievalService:
    def __init__(self) -> None:
        self._embedder = None
        self._collection = None
        self._lock = threading.Lock()

    def _ensure_loaded(self) -> None:
        # Fast path: already loaded, no locking overhead on every request.
        if self._embedder is not None and self._collection is not None:
            return

        # Slow path: only one thread should do the loading (ChromaDB's client
        # is not safe to initialize from two threads at once for the same path).
        with self._lock:
            if self._embedder is not None and self._collection is not None:
                return

            from chromadb import PersistentClient
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model '{settings.EMBEDDING_MODEL_NAME}'...")
            self._embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully.")

            if not os.path.isdir(settings.VECTOR_STORE_PATH):
                raise FileNotFoundError(
                    f"Vector store not found at '{settings.VECTOR_STORE_PATH}'. "
                    f"Run training/ingest_corpus.py first to build it."
                )

            client = PersistentClient(path=settings.VECTOR_STORE_PATH)
            collection = client.get_or_create_collection(name="financial_articles")

            if collection.count() == 0:
                raise FileNotFoundError(
                    "Vector store exists but is empty. Run training/ingest_corpus.py first."
                )
            logger.info(f"Vector store loaded with {collection.count()} articles.")
            self._collection = collection

    def find_similar(self, text: str, top_k: int, exclude_self: bool = False) -> SimilarArticlesResponse:
        self._ensure_loaded()

        query_embedding = self._embedder.encode([text]).tolist()

        # Ask for extra results so removed duplicates do not shrink the list below top_k.
        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=top_k + 5,
        )

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        query_norm = _normalize(text)
        matches = []
        removed = 0
        seen_titles = set()

        for article_id, doc, meta, distance in zip(ids, docs, metadatas, distances):
            # Chroma returns cosine DISTANCE (0 = identical); convert to similarity.
            similarity = round(max(1.0 - distance, 0.0), 4)
            title = meta.get("title", "Untitled")
            key = _normalize(title)

            # Benchmarks only: do not let a query retrieve itself.
            if exclude_self and (
                key == query_norm or _normalize(doc) == query_norm or similarity >= NEAR_DUPLICATE_THRESHOLD
            ):
                removed += 1
                continue

            # The same headline indexed twice is shown once.
            if key in seen_titles:
                removed += 1
                continue
            seen_titles.add(key)

            matches.append(
                SimilarArticleResult(
                    article_id=str(article_id),
                    title=title,
                    snippet=doc[:300],
                    source=meta.get("source"),
                    url=meta.get("url"),
                    published_at=meta.get("published_at"),
                    similarity_score=similarity,
                )
            )
            if len(matches) == top_k:
                break

        return SimilarArticlesResponse(results=matches, excluded_duplicates=removed)


retrieval_service = RetrievalService()