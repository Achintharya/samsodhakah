# Drafting Workflow

## Overview
The drafting workflow in Saṃśodhakaḥ enables grounded research paper section generation using Mistral API. This workflow integrates structured evidence retrieval, prompt building, and structured output generation.

---

## Architecture
The drafting workflow consists of the following components:

1. **Prompt Builders**: Modular prompt construction for different section types.
2. **Mistral Client**: Asynchronous integration with Mistral API.
3. **Drafting Workflow**: Orchestrates the entire drafting process.
4. **Structured Output Handling**: Converts structured Mistral outputs to prose.

---

## Components

### 1. Prompt Builders
Each section type has a dedicated prompt builder that constructs grounded prompts with evidence and citations.

#### Available Prompt Builders:
- `build_related_work_prompt`: For Related Work sections.
- `build_methodology_prompt`: For Methodology sections.
- `build_results_prompt`: For Results sections.
- `build_discussion_prompt`: For Discussion sections.
- `build_abstract_prompt`: For Abstract sections.

Each prompt builder:
- Takes a research topic, evidence units, and citations as input.
- Constructs a grounded prompt with structured evidence and citations.
- Logs token usage for monitoring.

---

### 2. Mistral Client
The `MistralClient` class provides asynchronous integration with the Mistral API.

#### Features:
- **Retry Logic**: Retries failed API calls up to `mistral_max_retries`.
- **Timeout Handling**: Configurable timeout for API calls.
- **Structured Response Handling**: Parses Mistral responses into structured outputs.
- **Token Tracking**: Tracks token usage for cost estimation.

#### Configuration:
- `MISTRAL_API_URL`: Base URL for Mistral API.
- `MISTRAL_API_KEY`: API key for authentication.
- `MISTRAL_MODEL`: Model to use for generation.
- `MISTRAL_MAX_TOKENS`: Maximum tokens for response.
- `MISTRAL_TEMPERATURE`: Sampling temperature.
- `MISTRAL_TIMEOUT`: Timeout for API calls.
- `MISTRAL_MAX_RETRIES`: Maximum number of retries.

---

### 3. Drafting Workflow
The `DraftingWorkflow` class orchestrates the entire drafting process.

#### Methods:
- `generate_section_outline`: Generates a structured outline for a research paper section.
- `generate_grounded_section`: Generates a grounded research section with evidence and citation support.

#### Workflow:
1. **Retrieve Evidence**: Gathers evidence units and semantic units from the semantic memory.
2. **Build Prompt**: Uses a specialized prompt builder to construct a grounded prompt.
3. **Generate Section**: Calls Mistral API to generate a structured section.
4. **Render Output**: Converts structured Mistral output to prose format.
5. **Verify Claims**: Extracts claims from the generated content for verification.
6. **Log Metrics**: Tracks token usage and other metrics.

---

### 4. Structured Output Handling
The workflow converts structured Mistral outputs to prose format for compatibility with existing systems.

#### Example Structured Output:
```json
{
  "section_title": "Related Work",
  "paragraphs": [
    {
      "text": "This section addresses the current state of research in the field of X.",
      "citations": [
        {"id": "cit1", "source_document": "Paper A", "content_preview": "...", "role": "supports", "confidence": 0.95}
      ],
      "evidence_ids": ["ev1", "ev2"],
      "confidence": 0.95,
      "provenance": {
        "source_documents": ["doc1", "doc2"],
        "retrieval_mode": "RELATED_WORK"
      }
    }
  ],
  "metadata": {
    "token_usage": {"total_tokens": 1200},
    "model": "mistral-tiny",
    "confidence": 0.95
  }
}
```

#### Rendering:
The `_render_structured_to_prose` method converts structured outputs to prose format:
```python
def _render_structured_to_prose(self, structured_result: Dict[str, Any]) -> str:
    prose_parts = [structured_result["section_title"]]
    for paragraph in structured_result["paragraphs"]:
        prose_parts.append(paragraph["text"])
    return "\n\n".join(prose_parts)
```

---

## Integration with Existing Systems
The drafting workflow integrates with existing systems to ensure backward compatibility:

- **Semantic Memory**: Retrieves evidence units and semantic units.
- **Retrieval System**: Uses scholarly retrieval to fetch relevant documents.
- **Verification Engine**: Extracts claims for verification.
- **Export System**: Renders structured outputs to prose for compatibility.

---

## Token Economy
The drafting workflow enforces strict token budgeting and compression:

- **PromptContextBuilder**: Ensures prompts are compressed and token-budgeted.
- **MistralClient**: Tracks token usage for cost estimation.
- **Token Metrics**: Logs token usage for monitoring and optimization.

---

## Usage Example
To generate a grounded section:

```python
section = await drafting_workflow.generate_grounded_section(
    document_id="doc123",
    section_type="related_work",
    topic="Machine Learning in Healthcare",
    related_work_id="doc456"
)
```

---

## Documentation Updates
This document reflects the current implementation of the drafting workflow, including:
- Integration with Mistral API.
- Structured output handling.
- Token economy and metrics.
- Backward compatibility with existing systems.