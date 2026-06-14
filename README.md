# Sales Rep Copilot

A RAG-based assistant for B2B sales reps. Ask natural language questions about customers and get grounded, data-driven answers powered by Claude API.

**Example questions:**
- "Summarize customer X"
- "Which Enterprise customers haven't ordered in 60 days?"
- "What products did customer Y buy in 2025?"

---

## Architecture

```
Sales rep → Streamlit UI (types question)
                ↓
          Embed question (sentence-transformers)
                ↓
          ChromaDB semantic search over customer profiles
                ↓
          Pre-compute aggregations (Python)
                ↓
          Claude API generates grounded answer
                ↓
          Answer displayed in Streamlit UI
```

---

## Stack

| Component | Tool |
|---|---|
| Data prep | pandas |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local) |
| Vector store | ChromaDB |
| LLM | Claude API (`claude-haiku-4-5`) |
| UI | Streamlit |

---

## Project Structure

```
RAG Project/
├── data/
│   ├── raw/            ← CSVs (not included — proprietary data)
│   └── processed/      ← Generated artifacts (not included)
├── src/
│   ├── data_prep.py        ← Phase 1: load & aggregate CSVs
│   ├── profile_builder.py  ← Phase 2: convert rows to text profiles
│   ├── embeddings.py       ← Phase 3: embed profiles into ChromaDB
│   ├── rag_pipeline.py     ← Phase 4: retrieval + answer generation
│   └── app.py              ← Phase 4: Streamlit UI
├── notebooks/
│   ├── data_prep.ipynb
│   └── profile_builder.ipynb
└── chroma_db/          ← Generated (not included)
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/gzagoreos/rag-sales-copilot.git
cd rag-sales-copilot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Prepare your data

Place your CSV files in `data/raw/`:
- `Customers.csv` — customer metadata (cus_code, cus_name, segment, salesperson, etc.)
- `Loads.csv` — transaction data (cus_code, amount, product code, date)
- `Product.csv` — product metadata (product code, product family)

Run the pipeline:

```bash
# Phase 1: aggregate data
python src/data_prep.py

# Phase 2: generate text profiles
python src/profile_builder.py

# Phase 3: embed and store in ChromaDB
python src/embeddings.py
```

### 5. Run the app

```bash
PYTHONPATH=src python3 -m streamlit run src/app.py
```

---

## How It Works

### Phase 1 — Data Preparation
Loads transaction CSVs, joins with product and customer dimensions, aggregates to one row per customer × product family × month.

### Phase 2 — Text Profile Generation
Converts each aggregated row into a pipe-separated text string:
```
Customer: CUSTOMER_A | Group: GROUP_A | Segment: Field Sales |
Employees: 131 | Job Type: Pharmaceuticals | Salesperson: SALESPERSON_A |
Product Family: EB | Month: 2023-01 | Revenue: €6,893 | Orders: 80
```

### Phase 3 — Embedding + Vector Store
Embeds all text profiles using `all-MiniLM-L6-v2` (local, no API cost) and stores them in a persistent ChromaDB collection with cosine similarity.

### Phase 4 — RAG Pipeline
1. User types a question
2. Question is embedded using the same model
3. ChromaDB finds semantically similar profiles
4. Aggregations (total, by month, by product) are pre-computed in Python
5. Retrieved profiles + aggregations are sent to Claude API
6. Claude generates a grounded natural language answer

---

## Notes

- Data is not included in this repo — replace with your own B2B transactional CSVs
- Embedding model: `all-MiniLM-L6-v2` (runs locally, no API cost)
- LLM: `claude-haiku-4-5` (cheapest Claude model, `temperature=0` for deterministic answers)
- ChromaDB collection is local-persistent under `chroma_db/`
