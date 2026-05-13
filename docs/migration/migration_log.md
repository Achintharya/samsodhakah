# Migration Log

> Tracking every preserved, rewritten, deprecated, and newly created system during the evolution from Akṣarajña → Saṃśodhakaḥ.

---

## Phase 0: Repository Initialization (2026-05-13)

| Action | Component | Status |
|---|---|---|
| Initialize | Fresh git repository | ✅ |
| Create | `.gitignore` | ✅ |
| Create | `README.md` — project vision and architecture | ✅ |
| Create | `LICENSE` — MIT | ✅ |
| Create | `CONTRIBUTING.md` — commit discipline | ✅ |

---

## Preservation Decisions

### Preserved (with refactoring)

| Component | Source | Target | Rationale |
|---|---|---|---|
| `AtomicFileManager` | `Akṣarajña backend/src/web_context_extract.py` | `backend/utils/file_manager.py` | Cross-platform atomic file operations with locking — well-written, reusable |
| `LocalStorageManager` | `Akṣarajña backend/src/storage_manager.py` | `backend/storage/local.py` | Clean abstraction for local filesystem storage |
| Web search (DuckDuckGo) | `Akṣarajña backend/src/web_context_extract.py` | `backend/ingestion/extractors/search.py` | Free, no-API-key search — valuable for research |
| Web search (Serper fallback) | `Akṣarajña backend/src/web_context_extract.py` | `backend/ingestion/extractors/search.py` | Premium fallback when DDG is rate-limited |
| HTML extraction (BeautifulSoup) | `Akṣarajña backend/src/web_context_extract.py` | `backend/ingestion/extractors/html.py` | Simple, dependency-light content extraction |
| FastAPI app foundation | `Akṣarajña backend/src/main.py` | `backend/main.py` (refactored) | Architecture patterns, not code |
| Frontend visual DNA | `Akṣarajña frontend/src/*.css` | `frontend/src/styles/variables.css` | Golden/dark warm scholarly aesthetic |
| Header component pattern | `Akṣarajña frontend/src/components/Header.js` | `frontend/src/components/Header.js` | Clean navigation pattern |
| MyArticles/List pattern | `Akṣarajña frontend/src/components/MyArticles.js` | `frontend/src/features/document-library/` | Modal-based document browsing pattern |
| ReactMarkdown rendering | `Akṣarajña frontend/src/components/ArticleGenerator.js` | `frontend/src/features/drafting-workspace/` | Markdown rendering for scholarly content |
| Job polling pattern | `Akṣarajña backend/src/main.py` | `backend/api/` | `/api/jobs/{id}` status tracking |

### Rewritten

| Component | Source | Target | Rationale |
|---|---|---|---|
| `main.py` (monolithic FastAPI) | `Akṣarajña backend/src/main.py` | `backend/api/*.py` | Decomposed into modular routers |
| `context_summarizer.py` | `Akṣarajña backend/src/context_summarizer.py` | `backend/ingestion/semantic/` | CrewAI monolith → modular lightweight pipeline |
| `article_writer.py` | `Akṣarajña backend/src/article_writer.py` | `backend/drafting/` | Tightly coupled → evidence-grounded modular drafting |
| `web_context_extract.py` | `Akṣarajña backend/src/web_context_extract.py` | `backend/ingestion/` | Monolithic → modular parsers + extractors |

### Deprecated / Removed

| Component | Source | Rationale |
|---|---|---|
| Supabase client | `Akṣarajña backend/src/supabase_client.py` | Not needed — local-first architecture |
| Supabase auth (JWT, JWKS) | `Akṣarajña backend/src/auth.py` | Not needed — no cloud dependencies |
| Auth UI (login/signup) | `Akṣarajña frontend/src/components/Auth.js` | Not needed — local-first, no authentication required |
| Guest mode logic | `Akṣarajña frontend/src/config/supabaseClient.js` | Not needed — no Supabase fallback |
| Async supabase proxy | `Akṣarajña frontend/src/config/supabaseClient.js` | Overengineered complexity |
| `sync_articles.py` | `Akṣarajña backend/sync_articles.py` | Deploy-specific, not needed in new architecture |
| Flask dependency | `Akṣarajña backend/requirements.txt` | No Flask endpoints in new system |
| CrewAI dependency | `Akṣarajña backend/requirements.txt` | Replaced with modular lightweight pipeline |

---

## Architecture Evolution Decisions

| Decision | Rationale |
|---|---|
| Local-only storage | Eliminate cloud dependency for research-grade local-first operation |
| SQLite for metadata | Lightweight, zero-config, sufficient for single-user research |
| In-memory FAISS for vectors | Fast local similarity search without server infrastructure |
| spaCy + regex for extraction | Deterministic, LLM-free semantic extraction |
| Pydantic strict typing | Runtime validation for all scientific data entities |
| Event-driven interfaces | Prepare for future distributed cognition without coupling now |
| Token economics tracking | Observability for LLM usage optimization |
| No auth system | Local-first single-user research tool — auth adds unnecessary complexity |

---

## Token Optimization Decisions

| Decision | Rationale |
|---|---|
| PromptContextBuilder | Centralized token budgeting and context compression |
| Never send raw documents to LLM | Compress to semantic units + evidence summaries only |
| Evidence prioritization by confidence | Reduce context size by ranking evidence relevance |
| Semantic deduplication | Remove redundant claims before prompt construction |
| Local embeddings for retrieval | Avoid LLM calls for basic similarity search |
| Caching at every layer | Avoid recomputation of embeddings, verifications, reranking |

---

## Future Extensibility Hooks

- Event schemas defined for message queue integration (Redis, Kafka, RabbitMQ)
- Plugin registry for custom parsers, extractors, verification strategies
- Multi-agent collaboration interfaces (literature review, hypothesis generation)
- Temporal scientific memory for versioned research state