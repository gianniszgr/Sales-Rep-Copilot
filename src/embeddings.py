# Phase 3 — Embeddings + Vector Store
# Embed text profiles with sentence-transformers and store in ChromaDB

from pathlib import Path
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILES_PATH = PROJECT_ROOT / "data" / "processed" / "customer_profiles.csv"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "customer_profiles"
MODEL_NAME = "all-MiniLM-L6-v2"

# ChromaDB add() has an internal limit per call; stay safely below it
CHROMA_BATCH_SIZE = 5000


def load_profiles(path: Path = PROFILES_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"text_profile", "cus_code", "cus_name", "Segment__c", "ProductFamily", "month", "SalesPerson"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"customer_profiles.csv is missing columns: {missing}")
    df = df.dropna(subset=["text_profile"])
    print(f"Loaded {len(df):,} profiles from {path.name}")
    return df


def embed_profiles(texts: list[str], model_name: str = MODEL_NAME) -> list:
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"Encoding {len(texts):,} texts (this takes a few minutes)...")
    embeddings = model.encode(texts, batch_size=256, show_progress_bar=True, convert_to_numpy=True)
    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings.tolist()


def store_in_chroma(
    df: pd.DataFrame,
    embeddings: list,
    collection_name: str = COLLECTION_NAME,
    chroma_path: Path = CHROMA_PATH,
    force_rebuild: bool = False,
) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(chroma_path))

    if force_rebuild:
        try:
            client.delete_collection(collection_name)
            print(f"Deleted existing collection '{collection_name}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    existing_count = collection.count()
    if existing_count > 0 and not force_rebuild:
        print(f"Collection '{collection_name}' already has {existing_count:,} vectors — skipping insert.")
        print("Pass force_rebuild=True to rebuild from scratch.")
        return collection

    ids = [
        f"{row.cus_code}_{row.ProductFamily}_{row.month}"
        for row in df.itertuples(index=False)
    ]

    metadatas = [
        {
            "cus_code": str(row.cus_code),
            "cus_name": str(row.cus_name),
            "segment": str(row.Segment__c),
            "product_family": str(row.ProductFamily),
            "month": str(row.month),
            "salesperson": str(row.SalesPerson),
        }
        for row in df.itertuples(index=False)
    ]

    documents = df["text_profile"].tolist()

    total = len(ids)
    print(f"Inserting {total:,} vectors into '{collection_name}' in batches of {CHROMA_BATCH_SIZE}...")

    for start in range(0, total, CHROMA_BATCH_SIZE):
        end = min(start + CHROMA_BATCH_SIZE, total)
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )
        print(f"  Inserted {end:,}/{total:,}")

    print(f"Done. Collection '{collection_name}' now has {collection.count():,} vectors.")
    return collection


def run(force_rebuild: bool = False) -> None:
    df = load_profiles()
    embeddings = embed_profiles(df["text_profile"].tolist())
    store_in_chroma(df, embeddings, force_rebuild=force_rebuild)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3: embed customer profiles into ChromaDB")
    parser.add_argument("--force-rebuild", action="store_true", help="Delete and rebuild the ChromaDB collection")
    args = parser.parse_args()
    run(force_rebuild=args.force_rebuild)
