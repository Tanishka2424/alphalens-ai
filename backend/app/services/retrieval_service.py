"""
Semantic similarity retrieval - embeds incoming text with a sentence-
transformer and searches a persistent ChromaDB collection of pre-indexed
financial articles for the closest matches by meaning (not keyword overlap).
"""
import os

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

    def _ensure_loaded(self) -> None:
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
        self._collection = client.get_or_create_collection(name="financial_articles")

        if self._collection.count() == 0:
            raise FileNotFoundError(
                "Vector store exists but is empty. Run training/ingest_corpus.py first."
            )
        logger.info(f"Vector store loaded with {self._collection.count()} articles.")

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