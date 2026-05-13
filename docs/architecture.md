# Saṃśodhakaḥ — System Architecture

## Overview

Saṃśodhakaḥ is a modular, evidence-grounded scientific research intelligence system. It transforms unstructured scientific documents into structured semantic knowledge, verifies claims against sources, and generates grounded scientific drafts.

## Architecture Principles

1. **Evidence-first**: Every claim must trace to a source document. Verification precedes any synthesis.
2. **Deterministic before LLM**: Rule-based extraction, lexical matching, and local embeddings are always preferred over LLM calls.
3. **Token-conscious**: No raw documents are ever sent to an LLM. Context is compressed, budgeted, and deduplicated.
4. **Modular boundaries**: Service boundaries are enforced. No monolithic orchestrators. Max 300 lines per module.
5. **Local-first**: Zero cloud dependencies. Filesystem storage, local embeddings, SQLite metadata.

## Data Flow

```
                    ┌─────────────────────────┐
                    │   Document Ingestion     │
                    │  (PDF/DOCX/MD/TXT/CSV)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Parser Abstraction     │
                    │   (section extraction)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Semantic Extraction    │
                    │  claims / methods /       │
                    │  metrics / equations /    │
                    │  entities / keyphrases   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Semantic Memory        │
                    │   (graphs + vectors)     │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │   BM25 Retrieval│  │   Vector Retrieval│  │   Metadata Filter│
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   Reranker              │
                    │   (evidence ranking)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Verification Engine    │
                    │  lexical → semantic →    │
                    │  numerical → consensus   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   PromptContextBuilder   │
                    │   (token budget +        │
                    │    semantic compression) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Draft Generator       │
                    │   (LLM with grounded     │
                    │    context only)         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Citation Linking      │
                    │   + Export (MD/DOCX/    │
                    │    LaTeX/BibTeX)        │
                    └─────────────────────────┘
```

## Module Descriptions

### 1. Ingestion (`backend/ingestion/`)

| Submodule | Responsibility |
|---|---|
| `parsers/` | Parse PDF, DOCX, MD, TXT, CSV into structured sections |
| `extractors/` | Web search (DDG/Serper) + HTML content extraction |
| `semantic/` | Extract claims, entities, keyphrases, equations using spaCy + regex |
| `pipeline.py` | Async orchestrator: parse → section → semantic unit → evidence unit |

### 2. Semantic Memory (`backend/semantic/`)

| Submodule | Responsibility |
|---|---|
| `memory.py` | Central semantic store — documents, sections, semantic units, evidence units |
| `graph.py` | Typed graph with nodes (papers, claims, equations, methods) and edges (supports, contradicts, cites, extends, derives_from) |
| `cache.py` | Multi-layer cache: embeddings, retrieval outputs, verification results |

### 3. Retrieval (`backend/retrieval/`)

| Submodule | Responsibility |
|---|---|
| `bm25.py` | Lexical retrieval using Okapi BM25 |
| `vector.py` | Dense retrieval using FAISS + sentence-transformers |
| `reranker.py` | Cross-encoder or lightweight reranking |
| `hybrid.py` | Orchestrator: BM25 → vector → rerank → consolidate |

### 4. Verification (`backend/verification/`)

| Submodule | Responsibility |
|---|---|
| `lexical.py` | Exact and fuzzy string matching against source |
| `semantic.py` | Embedding similarity verification |
| `numerical.py` | Number, metric, and statistical verification |
| `engine.py` | Multi-stage orchestrator producing full verification results |

### 5. Drafting (`backend/drafting/`)

| Submodule | Responsibility |
|---|---|
| `context_builder.py` | **PromptContextBuilder** — token budgeting, compression, evidence prioritization |
| `outline.py` | Topic → section structure planning |
| `evidence.py` | Evidence consolidation for each section |
| `generator.py` | LLM call with minimal, grounded context |
| `refinement.py` | Post-generation verification pass |

### 6. Storage (`backend/storage/`)

| Submodule | Responsibility |
|---|---|
| `local.py` | Filesystem storage with document indexing |
| `base.py` | Storage interface protocol |

### 7. Export (`backend/export/`)

| Submodule | Responsibility |
|---|---|
| `markdown.py` | Markdown export with citations |
| `docx.py` | DOCX export with proper formatting |
| `latex.py` | LaTeX export with bibliography |
| `bibtex.py` | BibTeX generation |

## Entity Model

```
Document
  ├── id, filename, doc_type
  ├── metadata (title, authors, year, doi, abstract)
  ├── status (pending → parsed → indexed)
  └── Sections
        ├── id, title, level, content, content_hash
        └── SemanticUnits
              ├── id, type (claim|methodology|metric|definition|equation|...)
              ├── content, normalized_content, confidence
              └── EvidenceUnits
                    ├── role (supports|contradicts|neutral)
                    ├── verification_method, verification_score
                    └── provenance_chain
```

## Token Economics

- **Max context per LLM call**: 4096 tokens
- **Compression target**: 30% of original context size
- **Evidence prioritization**: Rank by confidence score, include top-N
- **Deduplication**: Remove redundant claims before prompt construction
- **Caching**: Embeddings, retrieval outputs, verification results are all cached

## Event-Driven Architecture (Future)

All internal flows are designed as event pipelines even though currently synchronous:

- `document.uploaded` → `ingestion.started`
- `ingestion.completed` → `indexing.started`
- `retrieval.queried` → `verification.triggered`
- `verification.completed` → `draft.ready`
- `draft.generated` → `refinement.triggered`

This prepares for future Redis/Kafka/RabbitMQ integration without architectural changes.