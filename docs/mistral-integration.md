# Mistral Integration

## Overview
The Mistral integration in Saṃśodhakaḥ enables grounded research paper section generation using the Mistral API. This integration provides asynchronous, structured, and token-efficient drafting capabilities.

---

## Architecture
The Mistral integration consists of the following components:

1. **MistralClient**: Asynchronous client for Mistral API.
2. **Prompt Builders**: Modular prompt construction for different section types.
3. **Drafting Workflow**: Orchestrates the entire drafting process.

---

## MistralClient

### Features
- **Asynchronous API Calls**: Uses `httpx.AsyncClient` for non-blocking API calls.
- **Retry Logic**: Retries failed API calls up to `mistral_max_retries`.
- **Timeout Handling**: Configurable timeout for API calls.
- **Structured Response Handling**: Parses Mistral responses into structured outputs.
- **Token Tracking**: Tracks token usage for cost estimation.

### Configuration
The `MistralClient` is configured using environment variables and settings:

- **MISTRAL_API_URL**: Base URL for Mistral API (default: `https://api.mistral.ai/v1`).
- **MISTRAL_API_KEY**: API key for authentication (required).
- **MISTRAL_MODEL**: Model to use for generation (default: `mistral-tiny`).
- **MISTRAL_MAX_TOKENS**: Maximum tokens for response (default: `1024`).
- **MISTRAL_TEMPERATURE**: Sampling temperature (default: `0.7`).
- **MISTRAL_TIMEOUT**: Timeout for API calls (default: `30` seconds).
- **MISTRAL_MAX_RETRIES**: Maximum number of retries (default: `3`).

### Methods
- **call_mistral**: Makes an asynchronous call to Mistral API with retry logic.
- **generate_grounded_section**: Generates a grounded research section with structured context.
- **close**: Closes the HTTP client.

### Example Usage
```python
mistral_client = MistralClient()
structured_result = await mistral_client.generate_grounded_section(
    prompt="Generate a Related Work section on X.",
    structured_context={
        "topic": "Machine Learning in Healthcare",
        "evidence_units": evidence_units,
        "citations": citations,
        "retrieval_mode": "RELATED_WORK"
    }
)
```

---

## Structured Output Handling
The Mistral API returns structured outputs that include:
- **Section Title**: Title of the generated section.
- **Paragraphs**: List of paragraphs with citations, evidence IDs, confidence scores, and provenance.
- **Metadata**: Token usage, model, and confidence scores.

### Example Structured Output
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

---

## Integration with Drafting Workflow
The MistralClient is integrated into the `DraftingWorkflow` class to generate grounded research sections.

### Workflow Steps
1. **Retrieve Evidence**: Gathers evidence units and semantic units from the semantic memory.
2. **Build Prompt**: Uses a specialized prompt builder to construct a grounded prompt.
3. **Generate Section**: Calls Mistral API to generate a structured section.
4. **Render Output**: Converts structured Mistral output to prose format for compatibility with existing systems.
5. **Verify Claims**: Extracts claims from the generated content for verification.
6. **Log Metrics**: Tracks token usage and other metrics.

### Example Workflow
```python
section_result = await drafting_workflow.generate_grounded_section(
    document_id="doc123",
    section_type="related_work",
    topic="Machine Learning in Healthcare",
    related_work_id="doc456"
)
```

---

## Token Economy
The Mistral integration enforces strict token budgeting and compression:

- **PromptContextBuilder**: Ensures prompts are compressed and token-budgeted.
- **MistralClient**: Tracks token usage for cost estimation.
- **Token Metrics**: Logs token usage for monitoring and optimization.

### Token Usage Tracking
The `MistralClient` logs token usage for each API call:
```python
token_metrics.log(
    operation="draft_section",
    subsystem="mistral",
    input_tokens=len(prompt) // 4,
    context_size_chars=len(prompt),
    metadata={
        "section_type": section_type,
        "topic": topic,
        "token_count": structured_result["metadata"].get("token_usage", {}).get("total_tokens", 0)
    }
)
```

---

## Error Handling
The MistralClient includes robust error handling:

- **Retry Logic**: Retries failed API calls up to `mistral_max_retries`.
- **Timeout Handling**: Configurable timeout for API calls.
- **Logging**: Logs errors and warnings for debugging.

### Example Error Handling
```python
for attempt in range(self.max_retries):
    try:
        response = await self.client.post(
            "/chat/completions",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.warning(f"Attempt {attempt + 1} failed: {e}")
        if attempt == self.max_retries - 1:
            logger.error(f"Mistral API call failed after {self.max_retries} attempts")
            return None
```

---

## Documentation Updates
This document reflects the current implementation of Mistral integration, including:
- Asynchronous API calls with retry logic.
- Structured response handling.
- Token economy and metrics.
- Integration with the drafting workflow.
- Error handling and logging.

---

## Backward Compatibility
The Mistral integration is designed to ensure backward compatibility with existing systems:

- **Structured Output Rendering**: Converts structured Mistral outputs to prose format.
- **Token Budgeting**: Uses existing token budgeting mechanisms.
- **Logging**: Integrates with existing token metrics logging.

This ensures that existing workflows and systems continue to function without disruption.