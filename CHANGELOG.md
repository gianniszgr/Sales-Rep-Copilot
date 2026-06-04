# Changelog

All notable changes to this project are documented here.
Entries are added at the top (newest first) following the end-of-phase procedure.

---

## [2026-06-04] — Text Profile Generation Phase Complete

### Done
- Added save cell to notebooks/data_prep.ipynb (Section 4) — exports loads_monthly to data/processed/loads_monthly.csv (89,799 rows)
- Generated loads_monthly.csv by running the Phase 1 pipeline: data/processed/loads_monthly.csv saved and verified
- Generated text profiles from loads_monthly: one pipe-separated string per row covering customer identity, segment, salesperson, product family, month, revenue, and order count
- Saved 89,799 profiles to data/processed/customer_profiles.csv
- Populated src/profile_builder.py with clean functions (load_loads_monthly, build_text_profile, run) — loads from CSV, no raw data processing
- Created notebooks/profile_builder.ipynb for portfolio presentation

### Decisions
- Finding: initial implementation built a customer-level rollup (one row per customer, 3,810 rows) → Decision: reverted; embedding granularity stays at loads_monthly level (one row per customer × product family × month, 89,799 rows) — this preserves temporal and product-level signals for retrieval
- Finding: profile_builder.py was re-running the full 10M-row pipeline on every run → Decision: save loads_monthly.csv from data_prep.ipynb; profile_builder.py reads from data/processed/loads_monthly.csv directly
- Finding: loads filter is 2023+ in actual code (not 2020+ as originally stated in CLAUDE.md) → Decision: follow the actual code; CLAUDE.md corrected

### Deferred / Not Done
- data_prep.py not yet populated — logic lives in notebooks only; script translation deferred to end of project
- Text profile format not yet validated end-to-end against retrieval quality — will be tested in Phase 3/4

### Open Questions for Next Phase
- Which sentence-transformers model to use? (all-MiniLM-L6-v2 is the default, fast and good)
- ChromaDB collection name and persistence path?
- Top-N retrieval count for Phase 4?

---

## [2026-06-04] — Data Preparation Phase Complete

### Done
- Inspected data/raw/ — found 3 files: Customers.csv, Loads.csv, Product.csv (not 4 as originally planned)
- Loaded Customers.csv: 23,031 rows, selected 8 columns via usecols
- Loaded Loads.csv: 17M+ rows, filtered to 2020+, selected 5 columns via usecols
- Loaded Product.csv: 3 columns (vou_code, vou_label, ProductFamily)
- Built enrichment step: joined Loads with Product (on vou_code) and Customers (on cus_code)
- Built monthly aggregation: loads_monthly — one row per cus_code + product + month, with total_amt and order_count
- Explored and decided on embedding granularity: one row per customer for final RAG dataset
- All work done in notebooks/data_prep.ipynb

### Decisions
- Finding: Transactions.csv, Orders.csv, Contracts.csv not present in data/raw/ → Decision: use Loads.csv as the single transaction source; skip contract data entirely
- Finding: Loads.csv spans back to 2012 (17M rows) → Decision: filter to 2020+ to keep data commercially relevant
- Finding: cus_fin_code, cus_ext_ref, Segment_Abbreviation__c, RFMPersonas add noise without value for RAG → Decision: excluded from customers load via usecols
- Finding: enriching before aggregating makes dimension columns available in groupby → Decision: enrich first, aggregate second (not the other way around)
- Finding: monthly granularity enables temporal questions but creates many vectors per customer, risking incomplete retrieval → Decision: loads_monthly is an intermediate table; final embedding granularity is one row per customer
- Finding: vou_code was missing from groupby, breaking the product join → Decision: include vou_code in groupby keys alongside vou_label

### Deferred / Not Done
- Customer-level rollup (one row per customer) not yet built — first task of Phase 2
- data_prep.py not populated — all logic lives in notebooks/data_prep.ipynb; script translation deferred to end of project
- Contracts data skipped — file does not exist in data/raw/
- RFMPersonas excluded from pipeline — was in exclusion list; can be re-added if needed

### Open Questions for Next Phase
- Which fields to include in the text profile string per customer?
- Format: pipe-separated (structured) or natural language sentences?
- How to handle customers with no loads data (customers in Customers.csv with no match in Loads)?
- Should loads_monthly be saved to data/processed/ as a reference table?

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
