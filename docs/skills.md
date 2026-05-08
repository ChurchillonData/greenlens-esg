# Skills demonstrated by this project

This document maps the technical and analytical capabilities demonstrated by GreenLens to specific files, decisions, and project artefacts. It exists for two reasons. First, to help a reader who is evaluating this project quickly find the evidence behind each claimed capability. Second, to force the project author to articulate what each component of the work actually demonstrates, rather than relying on generic CV language.

The format is one capability per section, with concrete pointers. No skill appears here without a corresponding artefact in the repository.

---

## Domain understanding: ESG, regulatory frameworks, and the greenwashing problem

**Evidence.**
- The LinkedIn article on the FCA, CMA, and ECCTA regulatory shifts and what they imply for ESG data.
- Section 1 of the project documentation, which grounds the project in three specific 2024-2025 regulatory changes.
- The sector-specific claim taxonomy in section 3 of the project documentation, covering eight categories (net-zero commitments, emissions targets, methane reduction, renewables investment, scope 3 disclosure, just transition, biodiversity, climate lobbying), each with example claims and the type of external evidence they are tested against.
- The choice of NGO sources (InfluenceMap on lobbying, Carbon Tracker on capex alignment, ClientEarth on legal exposure, Global Witness on operations), reflecting the actual sources used by ESG analysts and regulators rather than generic news aggregation.

**What it demonstrates.** The candidate has read the underlying regulatory documents and the analyst literature, not just summary articles. The taxonomy and source selection reflect domain-specific knowledge of how oil and gas greenwashing actually manifests, rather than a generic NLP-on-text framing.

---

## ML system architecture for regulated industries

**Evidence.**
- Section 4 of the project documentation, including the architectural classification (4.4) explaining why GreenLens is not a RAG system and what it is instead.
- Decision D-001 in `DECISIONS.md`, comparing pure RAG, hybrid retrieval-plus-classification, and pure classification, with the rationale for the chosen architecture.
- The deliberate split between deterministic scoring and LLM rationale generation, documented in section 4.4.
- `src/greenlens/scoring/` and `src/greenlens/explainability/`, which implement the split in code.

**What it demonstrates.** The candidate can choose between architectural patterns based on what the problem actually requires, rather than defaulting to whatever is fashionable. The decision to keep the classification deterministic and use the LLM only for verbalisation is a non-obvious choice that reflects experience with auditability requirements in regulated contexts. This is the through-line with Govaxis AI, where the same principle applies to claims fraud detection.

---

## Explainability engineering for regulated ML systems

**Evidence.**
- Section 5 of the project documentation, the full explainability engineering specification covering output contract, source credibility weights, rationale generator design, frontend surface, and explanation evaluation.
- Decision D-012 in `DECISIONS.md`, on the rationale generator being constrained to verbalisation rather than decision.
- `src/greenlens/explainability/rationale_generator.py`, the LLM-driven generator with strict input/output constraints.
- `src/greenlens/explainability/validator.py`, the grounding validator that checks every rationale traces to evidence in the input before the rationale is returned.
- `src/greenlens/scoring/source_weights.py`, the version-controlled credibility weights table with documented rationale per source.
- The frontend explainability surface in `frontend/src/components/ClaimCard.jsx` and `frontend/src/components/EvidenceDrawer.jsx`, which surface the source weights, evidence snippets, and rationale grounding to the user.
- The explanation quality metrics (grounding pass rate, faithfulness, usefulness) reported in the technical blog post.

**What it demonstrates.** The candidate treats explainability as an engineering specification rather than a tagline. The output contract is fixed and audited. The LLM is constrained, validated, and replaceable. Source weights are explicit, version-controlled, and surfaced rather than hidden. Explanations are evaluated as a separate metric from classification accuracy. This is the depth of explainability work that production ML in regulated industries actually requires, and it is rarely demonstrated in portfolio projects.

---

## Multi-stage NLP pipelines with hybrid model selection

**Evidence.**
- The four-stage pipeline diagram (greenlens_architecture.png) and section 4.1 of the project documentation.
- `src/greenlens/nlp/relevance_filter.py` (ClimateBERT), `src/greenlens/nlp/claim_extractor.py` (OpenAI structured outputs), `src/greenlens/nlp/embeddings.py` (SBERT), `src/greenlens/nlp/reranker.py` (cross-encoder).
- Decisions D-005, D-006, D-007 in `DECISIONS.md`, documenting the model choices at each stage.

**What it demonstrates.** The candidate can compose multiple model types (small encoder, large language model, embedding model, cross-encoder) into a coherent pipeline, choosing each model for what it does well. This is more useful than calling one large model for everything, both in cost and in evaluability.

---

## Structured-output LLM engineering

**Evidence.**
- `src/greenlens/nlp/claim_extractor.py`, which uses OpenAI's JSON mode to convert hedged corporate prose into structured records (category, target, scope, time horizon).
- The prompt templates and schema definitions in the same module.
- Decision D-005 in `DECISIONS.md`, on provider selection and the trade-offs.
- The level 1 evaluation results (`notebooks/02_extraction_eval.ipynb`), demonstrating extraction accuracy on the structured fields.

**What it demonstrates.** The candidate can use LLMs as structured parsers rather than as open-ended generators. This is a different skill from prompt engineering for chat applications. It involves schema design, failure-mode handling, and reliability evaluation, all of which are documented in the level 1 evaluation.

---

## Evaluation discipline for ML systems

**Evidence.**
- Section 7 of the project documentation, the full evaluation methodology.
- `src/greenlens/eval/`, the three-level evaluation harness with `level1_extraction.py`, `level2_retrieval.py`, `level3_classification.py`, and `failure_modes.py`.
- `data/eval/labels.jsonl`, the published 150-claim hand-labelled set with documented labelling protocol.
- `src/greenlens/eval/label_tool.py`, the labelling tool used to build the dataset, also published.
- The failure mode taxonomy section in the technical blog post.

**What it demonstrates.** The candidate evaluates each pipeline stage independently, builds their own labelled data when public benchmarks do not fit the problem, follows a documented labelling protocol, and publishes failure modes alongside successes. This is the differentiator from a typical ML portfolio project, where evaluation is either skipped or reduced to a single benchmark number.

---

## Backend engineering with FastAPI

**Evidence.**
- `src/greenlens/api/`, the FastAPI application exposing endpoints for the company list, claim list per company, and claim detail with evidence.
- `tests/integration/test_api.py`, integration tests for the API.
- The Dockerfile at the repository root.
- `docker-compose.yml`, the one-command local run configuration.

**What it demonstrates.** The candidate can build a clean async API service, containerise it, and provide a one-command setup for someone reproducing the project. Engineering hygiene that is rare in ML portfolio projects.

---

## Frontend engineering with React

**Evidence.**
- `frontend/`, the React + Vite + Tailwind single-page application.
- The hosted live demo (link in README).
- The component structure showing the company selector, claim cards, and evidence drawer.
- Decision D-008 in `DECISIONS.md`, on the choice of React over Streamlit and the reasoning.

**What it demonstrates.** The candidate can build a production-shaped frontend rather than relying on Streamlit or notebook outputs. The visual storytelling is what makes the project legible to non-technical stakeholders, including most finance recruiters.

---

## Software engineering hygiene

**Evidence.**
- `pyproject.toml` with explicit dependency pinning.
- `.github/workflows/ci.yml`, the CI workflow running ruff, black, mypy, and pytest on every PR.
- `.pre-commit-config.yaml`, pre-commit hooks for lint and format.
- Branch protection on main, PR-only commits.
- Conventional commits used throughout the history.
- `CONTRIBUTING.md`, contribution guidelines even though this is a solo project.
- Test coverage in `tests/unit/` and `tests/integration/`.

**What it demonstrates.** The candidate works the way a senior engineer expects a teammate to work, even on a solo project. Recruiters who skim repos for hygiene cues find them.

---

## Technical writing for mixed audiences

**Evidence.**
- The LinkedIn article, written for a finance and ESG audience without ML background.
- The technical blog post (end-of-project deliverable), written for ML and data engineering audiences.
- The README, written for a recruiter or engineer doing a 90-second skim.
- The project documentation, written as a working document for a collaborator picking up the project.
- This file (`SKILLS.md`) and `DECISIONS.md`, written for a future reader trying to understand the choices made.

**What it demonstrates.** The candidate can match writing register to audience. The same project is described five different ways in five different documents, each appropriate to its reader. This is a non-trivial skill, especially in finance and ESG roles where translating between technical and non-technical audiences is the job.

---

## Strategic project framing

**Evidence.**
- The deliberate scope choice (oil and gas only, ten companies) documented in D-002.
- The deliberate evaluation choice (hand-labelled small set rather than benchmark) documented in D-003.
- The framing of GreenLens as the ESG counterpart to Govaxis AI (section 10 of the project documentation), establishing a coherent through-line across two projects.
- The two-piece writing strategy (LinkedIn at week one, technical blog at week four) documented in section 6 of the project documentation.

**What it demonstrates.** The candidate makes scope decisions strategically, not opportunistically. The project is sized to ship in four weeks while still being defensible in interviews. The connection to Govaxis is articulated explicitly so that two projects read as one coherent body of work rather than two unrelated experiments.

---

## How this file is maintained

New entries are added when new capabilities are implemented and have evidence in the repo. Entries are not added speculatively. If a capability listed here is later removed or changes, the entry is updated to reflect the actual state of the code. The file is reviewed at the end of each week.