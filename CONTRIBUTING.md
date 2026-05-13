# Contributing to Saṃśodhakaḥ

## Commit Discipline

This project follows strict commit discipline. Every commit must be:

1. **Atomic** — one logical change per commit
2. **Descriptive** — architecture-aware, implementation-specific
3. **Properly formatted** — using conventional commit format

### Commit Format

```
type(scope): description
```

### Types

| Type | Usage |
|---|---|
| `feat` | New feature or module |
| `refactor` | Code restructuring without feature change |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Tooling, dependencies, repo setup |
| `test` | Adding or updating tests |
| `perf` | Performance or token optimization |

### Examples

```
feat(semantic): implement evidence-unit extraction pipeline
refactor(frontend): migrate Akṣarajña UI into modular scholarly workspace
feat(retrieval): add hybrid BM25 + vector retrieval pipeline
feat(verification): implement multi-stage contradiction detection engine
docs(architecture): add semantic graph and ingestion flow documentation
chore(repo): initialize Saṃśodhakaḥ repository structure and tooling
```

### Anti-patterns

- ❌ Giant commits with unrelated changes
- ❌ Vague messages like "fix stuff" or "update code"
- ❌ Batch committing multiple features
- ❌ Leaving long uncommitted sessions

## Architecture Conventions

1. **Modularity**: No module >300 lines. Single responsibility per file.
2. **Typed contracts**: All interfaces use Pydantic models or Protocol classes.
3. **Dependency injection**: Use dependencies over global state.
4. **No monolithic orchestrators**: Compose small, focused services.
5. **Event-oriented**: Design internal flows as event pipelines, even if sync.

## Pull Request Process

1. Ensure all existing tests pass.
2. Add tests for new functionality.
3. Update documentation if changing public APIs.
4. Reference the migration log for architectural decisions.
5. Request review from maintainer.

## Development Setup

See [README.md](README.md) for setup instructions.

## Code Style

- Python: Follow PEP 8, use type hints, prefer Pydantic for data modeling.
- Frontend: Functional React components, custom hooks, CSS variables for theming.
- No Prettier/ESLint config is enforced, but maintain consistency with surrounding code.