# Saṃśodhakaḥ (सम्शोधकः)

> **researcher · investigator · one who inquires deeply**

Saṃśodhakaḥ is an **evidence-grounded scientific research intelligence system** — a modular platform that ingests scientific papers, extracts structured evidence, builds semantic research memory, verifies claims against source documents, and generates grounded scientific drafts.

This is a complete architectural evolution from the older Akṣarajña system, transforming an AI article generation tool into a research-grade scientific intelligence platform.

---

## Philosophy

Saṃśodhakaḥ is **not** a chatbot wrapper, simple RAG app, AI article generator, or generic writing SaaS.

Saṃśodhakaḥ **is**:

- **Evidence-first**: Every claim must trace to a source. Verification precedes synthesis.
- **Deterministic before LLM**: Rule-based extraction, lexical matching, and local embeddings are preferred before any LLM call.
- **Token-conscious**: Minimal prompts, compressed context, strict token budgets. Never send raw documents to an LLM.
- **Modular by design**: Service boundaries, typed contracts, dependency injection, repository pattern.
- **Local-first**: Prefer local filesystem storage, local embeddings, lightweight NLP pipelines.
- **Future-ready**: Architecture prepared for event-driven cognition, distributed workers, and multi-agent collaboration.

---

## Architecture

```
saṃśodhakaḥ/
├── backend/               # Python FastAPI backend
│   ├── api/               # REST API routers
│   ├── core/              # Core services (auth, dependencies)
│   ├── ingestion/         # Document parsing & extraction
│   │   ├── parsers/       # PDF, DOCX, MD, TXT, CSV
│   │   ├── extractors/    # Web search, HTML extraction
│   │   └── semantic/      # Claims, entities, keyphrases
│   ├── semantic/          # Semantic memory & graph storage
│   ├── retrieval/         # BM25 + Vector hybrid retrieval
│   ├── verification/      # Multi-stage claim verification
│   ├── drafting/          # Evidence-grounded draft generation
│   ├── citation/          # Citation extraction & formatting
│   ├── storage/           # Local filesystem storage
│   ├── export/            # MD, DOCX, LaTeX, BibTeX export
│   ├── workers/           # Background task definitions
│   ├── config/            # Pydantic settings
│   ├── utils/             # Logging, file mgmt, token tracking
│   └── models/            # Pydantic schemas
├── frontend/              # React scholarly workspace
│   └── src/
│       ├── styles/        # Design system tokens
│       ├── components/    # Shared UI components
│       ├── features/      # Feature modules
│       ├── hooks/         # Custom React hooks
│       ├── services/      # API service layer
│       └── layouts/       # Page layouts
├── docs/                  # Architecture & migration docs
└── runtime/               # Runtime data, cache, logs
```

### Core Data Flow

```
Document Upload
    ↓
Parser (PDF/DOCX/MD/TXT)
    ↓
Section Extraction
    ↓
Semantic Unit Extraction (claims, methods, metrics, equations...)
    ↓
Evidence Unit Creation
    ↓
[Indexing & Storage]
    ↓
Query → BM25 Retrieval → Vector Retrieval → Reranking → Evidence Consolidation
    ↓
Verification (lexical → semantic → numerical → consensus)
    ↓
PromptContextBuilder (token budget, compression, prioritization)
    ↓
Draft Generation (LLM with minimal, grounded context)
    ↓
Citation Linking & Export
```

---

## Key Features

| Feature | Description |
|---|---|
| **Document Ingestion** | PDF, DOCX, Markdown, TXT, CSV with section-level parsing |
| **Semantic Extraction** | Claims, entities, keyphrases, equations via lightweight NLP |
| **Hybrid Retrieval** | BM25 + vector embeddings + metadata filtering + reranking |
| **Verification Engine** | Lexical, semantic, numerical, contradiction detection |
| **Semantic Memory** | Claim graphs, citation graphs, evidence graphs |
| **Drafting Workspace** | Token-optimized, evidence-grounded, citation-aware |
| **Citation Management** | IEEE, ACM, APA, Springer + BibTeX export |
| **Export System** | Markdown, DOCX, LaTeX, PDF-ready |
| **Token Economics** | Per-operation tracking, compression metrics, budget enforcement |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
`python -m uvicorn backend.main:app --reload --port 8000`
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## Development Philosophy

1. **Correctness over speed** — Every component must be verifiably correct.
2. **Architecture quality** — Clean boundaries, single responsibility, testable interfaces.
3. **Semantic rigor** — Scientific knowledge as structured entities with typed relationships.
4. **Modularity** — No monolithic modules. Max 300 lines per file.
5. **Future extensibility** — Event-driven interfaces, plugin-ready design.

---

## License

MIT License — see [LICENSE](LICENSE)

## Author

**Achintharya**