"""
Numerical verification — extracts and compares numerical values, statistics, and metrics.
"""

from __future__ import annotations

import re
import logging
from typing import Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Numerical entity patterns
NUMBER_PATTERN = re.compile(r"""
    (?:
        \b\d+(?:\.\d+)?(?:%|percent|fold|x|times)\b |         # 42%, 3.5-fold
        \b(?:over|under|approximately|about|~)\s*\d+(?:\.\d+)?\b |  # over 100, ~50
        \b\d+(?:\.\d+)?\s*(?:million|billion|thousand|°C|K|MPa|GHz|ms|µs|ns|mm|cm|m|km)\b |  # 100 million, 25°C
        \b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b                       # plain numbers 42, 3.14, 1e-5
    )
""", re.VERBOSE | re.IGNORECASE)


class NumericalVerifier:
    """
    Extracts and verifies numerical claims against source documents.

    Compares numbers, percentages, units, and statistical values.
    """

    def verify(
        self,
        claim: str,
        source_text: str,
        source_id: str,
    ) -> dict:
        """
        Verify numerical claims in a statement against source text.

        Args:
            claim: Claim text containing numerical values.
            source_text: Source document text.
            source_id: Source identifier.

        Returns:
            Verification result with numerical comparison details.
        """
        claim_numbers = self._extract_numbers(claim)
        source_numbers = self._extract_numbers(source_text)

        if not claim_numbers:
            return {
                "source_id": source_id,
                "has_numerical_claim": False,
                "claim_numbers": [],
                "verdict": "no_numerical_content",
                "confidence": 1.0,
            }

        comparisons = []
        matches = 0
        total = len(claim_numbers)

        for cn in claim_numbers:
            best_match = None
            best_diff = float("inf")

            for sn in source_numbers:
                # Compare values with tolerance
                if cn["unit"] == sn["unit"]:
                    diff = abs(cn["value"] - sn["value"])
                    max_val = max(abs(cn["value"]), abs(sn["value"]), 1.0)
                    relative_diff = diff / max_val

                    if relative_diff < best_diff:
                        best_diff = relative_diff
                        best_match = sn

            if best_match and best_diff < settings.numerical_tolerance:
                matches += 1
                comparisons.append({
                    "claim_value": cn["raw"],
                    "claim_number": cn["value"],
                    "source_value": best_match["raw"],
                    "source_number": best_match["value"],
                    "relative_difference": round(best_diff, 4),
                    "unit": cn["unit"],
                    "match": True,
                })
            elif best_match:
                comparisons.append({
                    "claim_value": cn["raw"],
                    "claim_number": cn["value"],
                    "source_value": best_match["raw"],
                    "source_number": best_match["value"],
                    "relative_difference": round(best_diff, 4),
                    "unit": cn["unit"],
                    "match": False,
                })
            else:
                comparisons.append({
                    "claim_value": cn["raw"],
                    "claim_number": cn["value"],
                    "source_value": None,
                    "source_number": None,
                    "relative_difference": None,
                    "unit": cn["unit"],
                    "match": False,
                })

        match_rate = matches / total if total > 0 else 0

        if match_rate >= 0.8:
            verdict = "numerically_supported"
        elif match_rate >= 0.5:
            verdict = "partially_supported"
        elif match_rate > 0:
            verdict = "numerical_contradiction"
        else:
            verdict = "unverifiable"

        return {
            "source_id": source_id,
            "has_numerical_claim": True,
            "claim_numbers": claim_numbers,
            "comparisons": comparisons,
            "match_rate": round(match_rate, 4),
            "matches": matches,
            "total_numerical_claims": total,
            "verdict": verdict,
            "confidence": round(match_rate, 4),
        }

    def _extract_numbers(self, text: str) -> list[dict]:
        """Extract numerical values with units from text."""
        numbers = []
        for match in NUMBER_PATTERN.finditer(text):
            raw = match.group()
            value, unit = self._parse_number(raw)
            if value is not None:
                numbers.append({
                    "raw": raw,
                    "value": value,
                    "unit": unit or "unitless",
                })
        return numbers

    def _parse_number(self, token: str) -> tuple[Optional[float], Optional[str]]:
        """Parse a number token into value and unit."""
        token = token.strip().lower()

        # Multiplier suffixes
        multipliers = {
            "thousand": 1e3, "million": 1e6, "billion": 1e9,
            "k": 1e3, "m": 1e6, "b": 1e9,
        }

        # Remove common prefixes
        for prefix in ["over ", "under ", "approximately ", "about ", "~"]:
            if token.startswith(prefix):
                token = token[len(prefix):]
                break

        # Extract value and unit
        match = re.match(r"([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*(.*)", token)
        if not match:
            return None, None

        value_str = match.group(1)
        unit_str = match.group(2).strip()

        try:
            value = float(value_str)
        except ValueError:
            return None, None

        # Apply multiplier
        if unit_str in multipliers:
            value *= multipliers[unit_str]
            unit_str = ""

        # Normalize percentage
        if unit_str in ("%", "percent"):
            unit_str = "percent"

        return value, unit_str if unit_str else None


numerical_verifier = NumericalVerifier()