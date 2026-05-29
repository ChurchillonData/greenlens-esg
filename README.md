# Claimify ESG

Greenwashing detection for oil and gas sustainability reports. Scores corporate climate claims against NGO evidence and flags contradictions — with traceable rationale for every verdict.

---

## What it does

The pipeline ingests sustainability reports from ten oil and gas majors, extracts climate claims, retrieves relevant evidence from NGO sources (Carbon Tracker, InfluenceMap, ClientEarth, Global Witness, The Guardian), and scores each claim as `well_substantiated`, `weakly_substantiated`, or `contradicted`. An LLM generates a plain-language rationale for each verdict grounded in the retrieved evidence.

The frontend has three views:

- **Claims** — browse and filter scored claims per company with full evidence trails
- **Compare** — head-to-head claim analysis across companies and categories
- **Tracker** — historical pledge tracking with fulfilment verdicts

## Tech stack

| Layer | Tools |
|---|---|
| Ingestion | pdfplumber, BeautifulSoup, Guardian API |
| NLP | ClimateBERT (relevance filter), OpenAI (claim extraction + rationale) |
| Retrieval | SBERT embeddings, cross-encoder reranking |
| Frontend | React 18, Vite, Tailwind CSS |
| Serving | nginx (Docker), Vercel (hosted) |

## Getting started

### Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173
```

### Python pipeline

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -e ".[nlp]"
cp .env.example .env          # add OPENAI_API_KEY and GUARDIAN_API_KEY
```

Run the full pipeline:

```bash
python -m greenlens.ingestion.download_reports
python -m greenlens.retrieval.run_retrieval
python -m greenlens.scoring.run_scoring
python -m greenlens.scoring.run_rationale
python gen_frontend_data.py
```

### Docker

```bash
docker compose up --build     # serves frontend at http://localhost:8080
```

## Project structure

```
src/greenlens/
  ingestion/    PDF download and parsing, NGO feed fetching
  nlp/          Sentence splitting, ClimateBERT filter, claim extraction
  retrieval/    Corpus building, SBERT embeddings, reranking
  scoring/      LLM scorer, rationale generator, eval metrics
  eval/         Hand-labelled dataset and evaluation harness
frontend/src/   React components and utilities
scripts/        Historical claim extraction and tracker data generation
config/         Company list, NGO sources, pipeline settings
data/eval/      60-claim hand-labelled eval set (76.7% accuracy)
```

## License

MIT
