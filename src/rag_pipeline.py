# Phase 4 — RAG Pipeline
# Question → embed → ChromaDB retrieve → Claude API → answer

import os
import re
from pathlib import Path

import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "customer_profiles"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_N = 10
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a sales intelligence assistant. You answer questions about B2B customers \
using only the customer data provided to you. Be concise and specific. \
If the data does not contain enough information to answer, say so clearly."""


_customer_names_cache: set[str] | None = None


def get_collection(chroma_path: Path = CHROMA_PATH) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(chroma_path))
    return client.get_collection(name=COLLECTION_NAME)


def _load_customer_names(collection: chromadb.Collection) -> set[str]:
    global _customer_names_cache
    if _customer_names_cache is None:
        names: set[str] = set()
        batch_size = 5000
        offset = 0
        total = collection.count()
        while offset < total:
            batch = collection.get(limit=batch_size, offset=offset, include=["metadatas"])
            names.update(m["cus_name"] for m in batch["metadatas"])
            offset += batch_size
        _customer_names_cache = names
    return _customer_names_cache


def _extract_year(question: str) -> str | None:
    match = re.search(r"\b(20\d{2})\b", question)
    return match.group(1) if match else None


def _extract_customer_filter(question: str, collection: chromadb.Collection) -> dict | None:
    q_upper = question.upper()
    question_words = [w for w in q_upper.split() if len(w) >= 7]
    matches = [
        name for name in _load_customer_names(collection)
        if name.upper() in q_upper or any(w in name.upper() for w in question_words)
    ]
    if not matches:
        return None
    if len(matches) == 1:
        return {"cus_name": {"$eq": matches[0]}}
    return {"cus_name": {"$in": matches}}


def retrieve(question: str, collection: chromadb.Collection, top_n: int = TOP_N) -> list[dict]:
    where = _extract_customer_filter(question, collection)

    if where:
        # Fetch ALL records for this customer — needed for aggregation questions
        batch_size = 5000
        offset = 0
        all_docs, all_metas = [], []
        while True:
            batch = collection.get(
                where=where,
                limit=batch_size,
                offset=offset,
                include=["documents", "metadatas"],
            )
            if not batch["documents"]:
                break
            all_docs.extend(batch["documents"])
            all_metas.extend(batch["metadatas"])
            if len(batch["documents"]) < batch_size:
                break
            offset += batch_size

        # Filter by year if mentioned in the question
        year = _extract_year(question)
        if year:
            filtered = [(d, m) for d, m in zip(all_docs, all_metas) if m.get("month", "").startswith(year)]
            all_docs, all_metas = zip(*filtered) if filtered else ([], [])

        # Sort by month so Claude sees a chronological picture
        paired = sorted(zip(all_docs, all_metas), key=lambda x: x[1].get("month", ""))
        return [{"text": doc, "metadata": meta, "distance": None} for doc, meta in paired]

    # No customer identified — fall back to semantic top-N search
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([question], convert_to_numpy=True).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_n,
        include=["documents", "metadatas", "distances"],
    )
    profiles = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        profiles.append({"text": doc, "metadata": meta, "distance": dist})
    return profiles


def _compute_aggregations(profiles: list[dict]) -> str:
    """Parse revenue and orders from profile text and return pre-computed summary."""
    by_month: dict[str, dict] = {}
    by_product: dict[str, dict] = {}
    total_revenue = 0.0
    total_orders = 0

    for p in profiles:
        text = p["text"]
        month = p["metadata"].get("month", "")
        product = p["metadata"].get("product_family", "")

        rev_match = re.search(r"Revenue: €([\d,]+)", text)
        ord_match = re.search(r"Orders: (\d+)", text)
        rev = float(rev_match.group(1).replace(",", "")) if rev_match else 0.0
        orders = int(ord_match.group(1)) if ord_match else 0

        total_revenue += rev
        total_orders += orders

        if month:
            by_month.setdefault(month, {"revenue": 0.0, "orders": 0})
            by_month[month]["revenue"] += rev
            by_month[month]["orders"] += orders

        if product:
            by_product.setdefault(product, {"revenue": 0.0, "orders": 0})
            by_product[product]["revenue"] += rev
            by_product[product]["orders"] += orders

    lines = [f"Total across all records: Revenue €{total_revenue:,.0f} | Orders {total_orders:,}"]
    lines.append("By month:")
    for month in sorted(by_month):
        d = by_month[month]
        lines.append(f"  {month}: Revenue €{d['revenue']:,.0f} | Orders {d['orders']:,}")
    lines.append("By product family:")
    for product, d in sorted(by_product.items()):
        lines.append(f"  {product}: Revenue €{d['revenue']:,.0f} | Orders {d['orders']:,}")

    return "\n".join(lines)


def build_prompt(question: str, profiles: list[dict]) -> str:
    context_blocks = "\n\n".join(
        f"[Profile {i + 1}]\n{p['text']}" for i, p in enumerate(profiles)
    )
    aggregations = _compute_aggregations(profiles)
    return (
        f"Here are the most relevant customer profiles retrieved from the database:\n\n"
        f"{context_blocks}\n\n"
        f"Pre-computed aggregations (use these for any totals — do not re-sum from profiles):\n"
        f"{aggregations}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the data above."
    )


def generate_answer(prompt: str, api_key: str | None = None) -> str:
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def ask(question: str, top_n: int = TOP_N, api_key: str | None = None) -> dict:
    """End-to-end: question → retrieved profiles → answer."""
    collection = get_collection()
    profiles = retrieve(question, collection, top_n=top_n)
    prompt = build_prompt(question, profiles)
    answer = generate_answer(prompt, api_key=api_key)
    return {"answer": answer, "profiles": profiles}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 4: ask a question against the RAG pipeline")
    parser.add_argument("question", type=str, help="Natural language question about customers")
    parser.add_argument("--top-n", type=int, default=TOP_N, help="Number of profiles to retrieve")
    args = parser.parse_args()

    result = ask(args.question, top_n=args.top_n)
    print("\n--- Retrieved Profiles ---")
    for i, p in enumerate(result["profiles"]):
        print(f"\n[{i + 1}] {p['text']}")
    print("\n--- Answer ---")
    print(result["answer"])
