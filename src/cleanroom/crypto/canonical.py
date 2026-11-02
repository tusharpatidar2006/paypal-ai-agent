"""Canonical JSON serialization for deterministic signing and hashing.

Ensures that the same data structure always produces the same byte sequence.
"""
import json
from typing import Any
from decimal import Decimal


def to_canonical_json(obj: Any) -> str:
    """Convert object to canonical JSON string.
    
    Rules:
    - Keys are sorted
    - No whitespace
    - Consistent number formatting
    - Deterministic across Python versions
    
    Args:
        obj: Object to serialize (must be JSON-serializable)
        
    Returns:
        Canonical JSON string
    """
    
    def convert_value(v: Any) -> Any:
        """Convert values to JSON-safe types."""
        if isinstance(v, Decimal):
            # Format Decimal as string to preserve precision
            return str(v)
        if isinstance(v, dict):
            return {k: convert_value(val) for k, val in v.items()}
        if isinstance(v, (list, tuple)):
            return [convert_value(item) for item in v]
        return v
    
    converted = convert_value(obj)
    return json.dumps(
        converted,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def to_canonical_bytes(obj: Any) -> bytes:
    """Convert object to canonical JSON bytes.
    
    Args:
        obj: Object to serialize
        
    Returns:
        UTF-8 encoded canonical JSON
    """
    return to_canonical_json(obj).encode("utf-8")
