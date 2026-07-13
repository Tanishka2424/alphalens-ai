"""
Semantic similarity retrieval - embeds incoming text with a sentence-
transformer and searches a persistent ChromaDB collection of pre-indexed
financial articles for the closest matches by meaning (not keyword overlap).

Two-part lazy loading, same pattern as sentiment/credibility services:
- the embedding model loads once, cached
- the Chroma collection connects once, cached
Both stay empty/absent until ingest_corpus.py has been run to populate
the vector store - that's a separate one-time step, not part of a request.
"""
import os
import threading

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.retrieval import SimilarArticleResult, SimilarArticlesResponse

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self) -> None:
        self._embedder: SentenceTransformer | None = None
        self._collection = None
        self._lock = threading.Lock()

    def _ensure_loaded(self) -> None:
        # Fast path: already loaded, no locking overhead on every request.
        if self._embedder is not None and self._collection is not None:
            return

        # Slow path: only one thread should actually do the loading. Two
        # concurrent requests (e.g. /retrieval/similar-articles and
        # /consensus/analyze firing at the same time from the frontend)
        # both hitting this method for the first time is exactly what
        # caused a real crash in testing - ChromaDB's client isn't safe
        # to initialize from two threads at once for the same path.
        with self._lock:
            # Re-check inside the lock: another thread may have already
            # finished loading while this thread was waiting for the lock.
            if self._embedder is not None and self._collection is not None:
                return

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

    def find_similar(self, text: str, top_k: int) -> SimilarArticlesResponse:
        self._ensure_loaded()

        query_embedding = self._embedder.encode([text]).tolist()

        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        matches = []
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, distance in zip(docs, metadatas, distances):
            # Chroma returns cosine DISTANCE (0=identical); convert to a
            # similarity score (1=identical) for a more intuitive API response.
            similarity = round(max(1.0 - distance, 0.0), 4)
            matches.append(
                SimilarArticleResult(
                    title=meta.get("title", "Untitled"),
                    snippet=doc[:300],
                    source=meta.get("source"),
                    similarity_score=similarity,
                )
            )

        return SimilarArticlesResponse(results=matches)


retrieval_service = RetrievalService()