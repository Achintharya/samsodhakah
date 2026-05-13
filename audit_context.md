# Saṃśodhakaḥ — System Audit & Operationalization Context

## Current System Status

### Overall Verdict

Status: NEEDS MINOR STABILIZATION

Saṃśodhakaḥ is architecturally strong and modular, with working ingestion, retrieval, semantic memory, token budgeting, and export infrastructure.

The system is already usable for:

* evidence retrieval
* semantic search
* citation-aware exports
* semantic memory construction

However, it is NOT yet fully ready for active research paper writing because:

* drafting still contains placeholder generation logic
* PDF/DOCX parsing is incomplete
* verification engine is partially implemented
* frontend scholarly workflow is minimal

---

# 1. ARCHITECTURAL HEALTH

## Major Strengths

### Modular Architecture

The system has strong separation of concerns:

* ingestion/
* retrieval/
* drafting/
* verification/
* semantic/
* export/
* storage/

Architecture is clean and non-monolithic.

### Token-Conscious Design

PromptContextBuilder already exists and enforces:

* token budgeting
* semantic compression
* evidence prioritization
* deduplication

Token metrics/logging infrastructure also exists.

### Retrieval Infrastructure

Hybrid retrieval is implemented:

* BM25 retrieval
* vector retrieval
* reranking
* retrieval modes

Existing retrieval modes include:

* RELATED_WORK
* METHODOLOGY
* THEORY

### Export Infrastructure

Export support already exists for:

* Markdown
* LaTeX
* BibTeX
* DOCX

### Semantic Memory

System already supports:

* semantic units
* evidence units
* semantic persistence
* evidence-grounded retrieval

---

# 2. MAJOR CURRENT LIMITATIONS

## Placeholder Drafting Logic

Current drafting pipeline still uses simulated generation.

Placeholder generation MUST be fully replaced with real Mistral-powered grounded synthesis.

This is now the MOST important backend task.

---

## Missing PDF/DOCX Parsing

Parser infrastructure exists, but:

* PDF parser is incomplete
* DOCX parser is incomplete
* parsers are not fully integrated into ParserRegistry

This blocks real research-paper ingestion.

---

## Partial Verification Engine

Verification architecture exists but:

* lexical verification incomplete
* numerical verification incomplete
* contradiction logic incomplete
* confidence scoring partial

---

## Minimal Frontend Workflow

Frontend currently lacks:

* scholarly drafting workspace
* evidence explorer UX
* provenance visualization
* citation interaction
* drafting ergonomics

---

# 3. CURRENT WORKFLOW STATUS

| Workflow Step             | Status         | Notes                        |
| ------------------------- | -------------- | ---------------------------- |
| Upload Papers             | Mostly Working | Parser infrastructure exists |
| Parse Documents           | Partial        | PDF/DOCX incomplete          |
| Extract Semantic Evidence | Working        | Semantic units generated     |
| Store Semantic Memory     | Working        | Semantic persistence exists  |
| Retrieve Evidence         | Working        | Hybrid retrieval functional  |
| Generate Draft Sections   | Partial        | Placeholder synthesis        |
| Verify Claims             | Partial        | Verification incomplete      |
| Attach Citations          | Partial        | Basic grounding exists       |
| Export Papers             | Working        | Markdown/LaTeX/BibTeX/DOCX   |

---

# 4. TOKEN ECONOMY STATUS

## Existing Strengths

Current system already supports:

* token budgeting
* semantic compression
* evidence deduplication
* retrieval narrowing
* token metrics logging

This architecture should be preserved.

---

## Existing Weaknesses

### Retrieval Waste

Hybrid retrieval currently retrieves:
top_k * 2

This creates unnecessary token overhead.

### Static Budgeting

Token budgets are fixed and not adaptive.

### Placeholder Drafting

Simulated generation bypasses real token constraints.

---

# 5. PRIMARY OPERATIONALIZATION GOALS

Saṃśodhakaḥ is now transitioning from:
“architecture construction”

to:

“usable scientific paper-writing system”

The benchmark is now:

Can Achinth use this system to help write a publishable research paper?

---

# 6. IMMEDIATE IMPLEMENTATION PRIORITIES

## PRIORITY 1 — Robust PDF/DOCX Ingestion

### PDF Parsing

Implement robust PDF parsing using:

* pypdf
* pymupdf (fallback if needed)
* pdfplumber if necessary

Required extraction:

* title
* authors
* abstract
* section hierarchy
* citations
* references
* equations
* semantic units

### DOCX Parsing

Use:

* python-docx

Extract:

* headings
* paragraphs
* citations
* tables
* semantic units

### Ingestion Logging

Create:
`/runtime/ingestion_logs`

Log:

* extraction failures
* malformed structures
* parser confidence
* semantic counts
* missing sections

---

# 7. PRIORITY 2 — REAL MISTRAL-POWERED DRAFTING

## Replace ALL Placeholder Logic

Remove:

* simulated generation
* fake drafting
* placeholder synthesis

---

## Mistral Integration

Create:
`/backend/drafting/mistral_client.py`

Requirements:

* async support
* retry handling
* timeout handling
* token tracking
* cost estimation
* structured responses

Use Mistral ONLY for:

* grounded synthesis
* section drafting
* literature review generation
* refinement

DO NOT use Mistral for:

* parsing
* extraction
* retrieval
* deterministic verification

---

## Critical Grounding Rule

Mistral MUST NEVER receive:

* full papers
* raw retrieval dumps
* giant contexts
* full semantic memory

Mistral should ONLY receive:

* compressed evidence
* ranked semantic units
* relevant citations
* structured retrieval summaries

---

# 8. PRIORITY 3 — VERIFICATION ENGINE

Implement:

* lexical verification
* semantic verification
* citation support verification
* contradiction warnings
* confidence scoring

Initial verification goals:

* evidence existence
* semantic support
* contradiction detection
* confidence estimation

Do NOT overengineer verification initially.

---

# 9. PRIORITY 4 — FRONTEND SCHOLARLY WORKSPACE

Frontend should become:

* semantic writing IDE
* research notebook
* evidence-grounded drafting workspace

NOT:

* SaaS dashboard
* analytics platform
* chatbot UI

---

## Core Frontend Areas

Implement:

1. Paper Upload Panel
2. Semantic Search
3. Evidence Explorer
4. Drafting Workspace
5. Citation Sidebar
6. Verification Panel
7. Export Panel

---

## Frontend Design Philosophy

Maintain:

* minimal UI
* scholarly tone
* typography-first design
* calm spacing
* restrained palette
* evidence visibility

Avoid:

* dashboard clutter
* flashy gradients
* excessive cards
* unnecessary widgets

---

# 10. REAL RESEARCH TESTING

As soon as:

* ingestion works
* retrieval works
* drafting works

Immediately begin testing using:

* Tvastr docs
* architecture notes
* technical references
* uploaded papers
* methodology notes

---

# 11. REAL-WORLD BENCHMARKS

Saṃśodhakaḥ should eventually be able to:

* generate Related Work
* generate Methodology sections
* synthesize grounded summaries
* retrieve supporting evidence
* attach citations
* export usable drafts

---

# 12. ENGINEERING PHILOSOPHY GOING FORWARD

DO:

* prioritize usability
* prioritize workflow quality
* prioritize retrieval quality
* prioritize grounded drafting
* prioritize verification quality

DO NOT:

* endlessly expand abstractions
* build speculative cognition systems
* overengineer orchestration
* optimize hypothetical scaling

---

# 13. PRIMARY SUCCESS CONDITION

Saṃśodhakaḥ succeeds if:
Achinth can realistically use it to:

* write literature reviews
* draft methodology sections
* generate grounded research drafts
* retrieve supporting evidence
* verify claims
* export usable papers

using:

* uploaded research papers
* Tvastr documentation
* technical references
* semantic retrieval workflows
