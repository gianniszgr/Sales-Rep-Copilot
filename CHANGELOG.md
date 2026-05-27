# Changelog

All notable changes to this project are documented here.
Entries are added at the top (newest first) following the end-of-phase procedure.

---

## [2026-05-27] — Folder Structure Phase Complete

### Done
- Created CHANGELOG.md (this file)
- Created project folder structure: data/raw, data/processed, src/, chroma_db/, mlflow_runs/, docker/
- Created .gitignore (ignores .env, data/raw/, chroma_db/, mlflow_runs/, __pycache__, .DS_Store)
- Created requirements.txt with all phase dependencies (pandas, sentence-transformers, chromadb, langchain, anthropic, streamlit, mlflow)
- Created README.md with architecture overview and setup instructions
- Created .env.example with ANTHROPIC_API_KEY placeholder
- Scaffolded empty src/ files: data_prep.py, profile_builder.py, embeddings.py, rag_pipeline.py, app.py
- Scaffolded empty docker/Dockerfile and docker/docker-compose.yml
- Added .gitkeep to data/raw/ and data/processed/ to track empty dirs in git

### Decisions
- Finding: data/raw/ contains real Edenred customer data → Decision: gitignore data/raw/ entirely to prevent accidental commit of sensitive data
- Finding: chroma_db/ and mlflow_runs/ are generated artifacts → Decision: gitignore both; they are local-persistent but not committed
- Finding: src/ files map 1:1 to phases → Decision: keep this structure so each phase has a clear, single owner file
- Finding: we are starting directly on main → Decision: no separate setup branch; folder structure committed directly to main

### Deferred / Not Done
- docker/Dockerfile and docker-compose.yml are placeholders — filled in Phase 5
- README.md architecture diagram image not yet added — deferred to Phase 5

### Open Questions for Next Phase
- What are the exact column names and data quality of the 4 CSVs? Need to inspect before writing merge logic
- Are there customers in Transactions/Orders/Contracts with no match in Customers.csv? Need to decide on join type (inner vs left)
- What date range does the data cover? Needed for "last N days" query logic

---
