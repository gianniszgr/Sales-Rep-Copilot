# Sales Rep Copilot

A RAG-based assistant for B2B sales reps. Ask natural language questions about customers and get grounded, data-driven answers powered by Claude API.

## Architecture

```
Sales rep → Streamlit UI (types question)
                ↓
          LangChain pipeline
                ↓
          ChromaDB retrieval (semantic search over customer profiles)
                ↓
          Claude API generates grounded answer
                ↓
          Answer displayed in Streamlit UI
```

## Stack

| Component | Tool |
|---|---|
| Data prep | pandas |
| Embeddings | sentence-transformers (local) |
| Vector store | ChromaDB |
| Orchestration | LangChain |
| LLM | Claude API |
| UI | Streamlit |
| Experiment tracking | MLflow |
| Containerization | Docker |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
```

## Run

```bash
streamlit run src/app.py
```

## Docker

```bash
docker-compose -f docker/docker-compose.yml up
```
