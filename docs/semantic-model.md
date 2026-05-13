# Semantic Data Model

## Core Entities

### Document
The top-level entity representing an ingested scientific paper or document.

| Field | Type | Description |
|---|---|---|
| `id` | string (12-char hex) | Unique identifier |
| `filename` | string | Original filename |
| `doc_type` | enum | pdf, docx, markdown, txt, csv, html |
| `status` | enum | pending, parsing, parsed, semantic_extraction, indexed, failed |
| `metadata` | DocumentMetadata | Title, authors, year, journal, DOI, abstract |
| `section_count` | int | Number of extracted sections |
| `semantic_unit_count` | int | Number of extracted semantic units |
| `content_hash` | string | SHA-256 hash of raw content |
| `storage_path` | string | Path in local filesystem |

### Section
A hierarchical section within a document.

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `document_id` | string | Parent document |
| `title` | string | Section heading |
| `level` | int | Heading depth (1 = h1, 2 = h2) |
| `content` | string | Raw section text |
| `content_hash` | string | For deduplication |
| `order` | int | Position in document |
| `parent_section_id` | string? | Parent section (for nested hierarchy) |

### SemanticUnit
An atomic knowledge piece extracted from a section.

**Types:**
- `claim` — A positive assertion/statement
- `methodology` — Description of a method or approach  
- `metric` — A quantitative measurement or evaluation
- `definition` — Definition of a term or concept
- `equation` — A mathematical expression
- `observation` — An empirical observation
- `hypothesis` — A proposed explanation
- `limitation` — A stated limitation or caveat
- `experimental_result` — A specific experimental finding

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `document_id` | string | Source document |
| `section_id` | string | Source section |
| `unit_type` | SemanticUnitType | The type of semantic unit |
| `content` | string | Extracted text |
| `normalized_content` | string | For deduplication matching |
| `confidence` | float (0-1) | Extraction confidence |
| `embedding` | [float]? | Vector embedding |
| `page_references` | [int] | Page numbers |

### EvidenceUnit
A verified link between a claim and source evidence.

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `claim_id` | string | The claim being evidenced |
| `source_document_id` | string | Provenance document |
| `source_section_id` | string | Provenance section |
| `source_semantic_unit_id` | string | Provenance semantic unit |
| `content` | string | The supporting/contradicting text |
| `role` | enum | supports, contradicts, neutral, weakens, strengthens |
| `confidence` | float (0-1) | Verification confidence |
| `verification_method` | enum | lexical, semantic, numerical, consensus, citation |

### Claim
A structured assertion that can be verified.

Claims are a subset of SemanticUnits (type=claim) but may also be:
- Extracted from documents during ingestion
- Generated during drafting
- Inferred during semantic analysis

### Citation
A reference extracted from a document.

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `document_id` | string | Source document |
| `raw_text` | string | Original citation text |
| `authors` | [string] | Parsed author list |
| `title` | string? | Cited work title |
| `year` | int? | Publication year |
| `doi` | string? | Digital Object Identifier |

### Metric
A quantitative measure or evaluation result.

Metrics may be:
- Extracted from experimental results
- Calculated during verification (confidence scores)
- Tracked during token economics

### Equation
A mathematical expression extracted from a document.

Detected via regex patterns for:
- Inline equations ($...$)
- Display equations ($$...$$)
- Common mathematical notation

### Method
A described methodology or approach.

Typically found in "Methodology" or "Methods" sections.

### ExperimentalResult
A specific experimental finding with numerical values.

## Entity Relationships

```
Document ──contains──▶ Section ──contains──▶ SemanticUnit
                                                │
                                                ├── type=claim ──▶ Claim
                                                ├── type=metric ──▶ Metric
                                                ├── type=equation ──▶ Equation
                                                ├── type=methodology ──▶ Method
                                                └── type=experimental_result ──▶ ExperimentalResult

Claim ──verified_by──▶ EvidenceUnit ──references──▶ Document
                                                     │
                                                     └── contains ──▶ Citation

Claim ──supports/contradicts──▶ Claim  (via graph edges)
Document ──cites──▶ Document    (via citation graph)
Method ──used_in──▶ Experiment  (via method graph)
```

## Graph Edge Types

| Edge | Source Node | Target Node | Description |
|---|---|---|---|
| `supports` | Claim | Claim | One claim supports another |
| `contradicts` | Claim | Claim | Claims are contradictory |
| `cites` | Document | Document | Citation relationship |
| `extends` | Method | Method | Methodological extension |
| `derives_from` | Claim | Claim | Derived conclusion |
| `validates` | Experiment | Claim | Experimental validation |
| `weakens` | EvidenceUnit | Claim | Evidence weakens a claim |
| `uses_method` | Experiment | Method | Experiment applies a method |
| `reports_metric` | Experiment | Metric | Experiment reports a metric |