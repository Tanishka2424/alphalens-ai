"""
Ingests SEntFiN-v1.1.csv into a persistent ChromaDB collection for semantic
similarity retrieval (Phase 3).

Source: Kaggle "Aspect based Sentiment Analysis for Financial News"
(Ankur Sinha / SEntFiN 1.0) - 10,700+ real financial news headlines,
India-market-skewed (worth noting in the writeup, not a hidden flaw).

Columns confirmed manually before writing this (same discipline as Phase 2):
S No. | Title | Decisions (per-entity sentiment JSON, e.g. {"Sebi": "neutral"}) | Words
"""
import json
import os

import pandas as pd
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

RAW_PATH = "data/SEntFiN-v1.1.csv"
VECTOR_STORE_PATH = "vector_store"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 500


def main() -> None:
    df = pd.read_csv(RAW_PATH)
    print(f"Loaded {len(df)} rows")

    before = len(df)
    df = df.dropna(subset=["Title"])
    df = df.drop_duplicates(subset=["Title"])
    print(f"Dropped {before - len(df)} null/duplicate rows -> {len(df)} remain")

    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Embedding model loaded.")

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    client = PersistentClient(path=VECTOR_STORE_PATH)
    try:
        client.delete_collection(name="financial_articles")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name="financial_articles",
        metadata={"hnsw:space": "cosine"},  # explicit, not Chroma's L2 default -
                                              # makes "1 - distance" an exact cosine similarity
    )

    titles = df["Title"].tolist()
    ids = [str(sno) for sno in df["S No."].tolist()]

    metadatas = []
    for decisions_raw in df["Decisions"].tolist():
        try:
            entities = json.loads(decisions_raw)
            entity_summary = ", ".join(f"{k}:{v}" for k, v in entities.items())
        except (json.JSONDecodeError, TypeError):
            entity_summary = ""
        metadatas.append({"title": "", "source": "SEntFiN dataset (India-market financial news)", "entities": entity_summary})

    for i, meta in enumerate(metadatas):
        meta["title"] = titles[i]

    print(f"Embedding and inserting {len(titles)} headlines in batches of {BATCH_SIZE}...")
    for start in range(0, len(titles), BATCH_SIZE):
        end = start + BATCH_SIZE
        batch_titles = titles[start:end]
        batch_ids = ids[start:end]
        batch_metadatas = metadatas[start:end]

        embeddings = embedder.encode(batch_titles).tolist()

        collection.add(
            documents=batch_titles,
            embeddings=embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids,
        )
        print(f"  Inserted {min(end, len(titles))}/{len(titles)}")

    print(f"\nDone. Collection now has {collection.count()} documents at '{VECTOR_STORE_PATH}'")

    test_query = titles[0]
    test_embedding = embedder.encode([test_query]).tolist()
    result = collection.query(query_embeddings=test_embedding, n_results=1)
    print(f"\nSanity check - querying with: '{test_query}'")
    print(f"Top match: '{result['documents'][0][0]}' (distance={result['distances'][0][0]:.4f})")


if __name__ == "__main__":
    main()