"""
Mistral Client — asynchronous integration with Mistral API for grounded drafting.
"""

from __future__ import annotations
import logging
import os
import json
from typing import Optional, Dict, Any, List
import httpx
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class MistralClient:
    """
    Asynchronous client for Mistral API with retry logic, timeout handling,
    and structured response handling.
    """

    def __init__(self) -> None:
        self.base_url = settings.mistral_api_url
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.timeout = settings.mistral_timeout
        self.max_retries = settings.mistral_max_retries
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout
        )

    async def call_mistral(
        self,
        prompt: str,
        model: str = settings.mistral_model,
        max_tokens: int = settings.mistral_max_tokens,
        temperature: float = settings.mistral_temperature
    ) -> Optional[Dict[str, Any]]:
        """
        Make an asynchronous call to Mistral API with retry logic.

        Args:
            prompt: Input prompt for Mistral
            model: Model to use
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature

        Returns:
            JSON response from Mistral or None if failed
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

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
            except Exception as e:
                logger.error(f"Unexpected error calling Mistral: {e}")
                return None

        return None

    async def generate_grounded_section(
        self,
        prompt: str,
        structured_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a grounded research section with structured context.

        Args:
            prompt: Research topic prompt
            structured_context: Context with evidence, citations, and provenance

        Returns:
            Structured generation result with citations, evidence, and confidence
        """
        try:
            response = await self.call_mistral(prompt)
            if not response:
                return None

            # Parse structured response
            generated_content = response["choices"][0]["message"]["content"]

            # Convert to structured format
            structured_output = {
                "section_title": structured_context.get("topic", "Generated Section"),
                "paragraphs": self._parse_paragraphs(generated_content, structured_context),
                "metadata": {
                    "token_usage": response.get("usage", {}),
                    "model": response.get("model", "unknown"),
                    "confidence": 0.95  # Default confidence
                }
            }

            return structured_output
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            return None

    def _parse_paragraphs(
        self,
        content: str,
        structured_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse raw content into structured paragraphs with citations and provenance.

        Args:
            content: Raw generated content
            structured_context: Context with evidence and citations

        Returns:
            List of structured paragraphs
        """
        paragraphs = []
        evidence_units = structured_context.get("evidence_units", [])
        citations = structured_context.get("citations", [])

        # Simple paragraph splitting
        raw_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        for i, paragraph in enumerate(raw_paragraphs):
            # Assign citations and evidence based on context
            citations_for_para = citations[:min(2, len(citations))]
            evidence_for_para = evidence_units[:min(3, len(evidence_units))]

            paragraphs.append({
                "text": paragraph,
                "citations": citations_for_para,
                "evidence_ids": [ev["id"] for ev in evidence_for_para],
                "confidence": 0.95,
                "provenance": {
                    "source_documents": [ev.get("source_document_id") for ev in evidence_for_para],
                    "retrieval_mode": structured_context.get("retrieval_mode", "unknown")
                }
            })

        return paragraphs

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()