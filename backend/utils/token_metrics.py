"""
Token economics tracking and observability.
Tracks token usage across all subsystems for optimization.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import logging

from backend.utils.file_manager import file_manager

logger = logging.getLogger(__name__)


class TokenMetrics:
    """Tracks token usage across retrieval, drafting, verification cycles."""

    def __init__(self) -> None:
        self.log_path = Path("runtime/logs/token_metrics.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        operation: str,          # retrieval | draft_section | verification | export
        subsystem: str,          # which module performed the operation
        input_tokens: int,
        output_tokens: int = 0,
        context_size_chars: int = 0,
        compressed_size_chars: int = 0,
        compression_ratio: Optional[float] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Log a token usage event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "subsystem": subsystem,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "context_size_chars": context_size_chars,
            "compressed_size_chars": compressed_size_chars,
            "compression_ratio": compression_ratio or (
                1.0 - (compressed_size_chars / context_size_chars)
                if context_size_chars > 0 else 0.0
            ),
            "metadata": metadata or {},
        }

        # Append to JSONL log
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write token metrics: {e}")

    def get_summary(self) -> dict:
        """Get summary statistics from the token log."""
        if not self.log_path.exists():
            return {}

        total_input = 0
        total_output = 0
        operation_counts = {}
        compression_ratios = []

        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        total_input += entry.get("input_tokens", 0)
                        total_output += entry.get("output_tokens", 0)
                        op = entry.get("operation", "unknown")
                        operation_counts[op] = operation_counts.get(op, 0) + 1
                        if entry.get("compression_ratio", 0) > 0:
                            compression_ratios.append(entry["compression_ratio"])
        except Exception as e:
            logger.warning(f"Failed to read token metrics: {e}")

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "operation_breakdown": operation_counts,
            "avg_compression_ratio": (
                sum(compression_ratios) / len(compression_ratios)
                if compression_ratios else 0.0
            ),
        }


# Global singleton
token_metrics = TokenMetrics()