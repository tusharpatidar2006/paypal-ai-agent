"""Rule-based detection for known attack patterns."""
import re
from typing import Optional


class RuleDetector:
    """Rule-based prompt injection detector."""
    
    def __init__(self):
        """Initialize rule detector with patterns."""
        # Prompt injection patterns
        self.patterns = [
            # Direct instruction attempts
            (r"ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|rules?)", 0.9),
            (r"disregard\s+(previous|all|above|prior)", 0.9),
            (r"forget\s+(everything|all|previous|instructions?)", 0.85),
            
            # System message attempts
            (r"system\s*:\s*you\s+are", 0.85),
            (r"<\s*system\s*>", 0.85),
            (r"\[SYSTEM\]", 0.85),
            
            # Role manipulation
            (r"you\s+are\s+now\s+(a|an)", 0.8),
            (r"new\s+role\s*:", 0.8),
            (r"act\s+as\s+(a|an|if)", 0.75),
            (r"pretend\s+(you|to)\s+(are|be)", 0.75),
            
            # Override attempts
            (r"override\s+(all|security|previous)", 0.9),
            (r"disable\s+(security|checks?|filters?)", 0.9),
            
            # Information exfiltration
            (r"send\s+(this|data|information)\s+to", 0.85),
            (r"transmit\s+to", 0.85),
            (r"forward\s+to", 0.8),
            
            # Command injection
            (r"execute\s+command", 0.85),
            (r"run\s+code", 0.85),
            
            # Address/payee manipulation keywords
            (r"change\s+(address|shipping|destination)", 0.7),
            (r"ship\s+to\s+[0-9]+", 0.7),
            (r"send\s+payment\s+to", 0.8),
            (r"paypal\.me/", 0.75),
            
            # Obfuscation indicators
            (r"<!--.*(?:ignore|system|override).*-->", 0.8),
            (r"%%.*(?:ignore|system|override).*%%", 0.8),
            
            # Prompt leakage attempts
            (r"repeat\s+(the|your)\s+(system|instructions?)", 0.85),
            (r"what\s+(are|is)\s+your\s+(system|instructions?)", 0.8),
            (r"show\s+(me\s+)?(the|your)\s+prompt", 0.85),
        ]
        
        # Compile patterns
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), score)
            for pattern, score in self.patterns
        ]
    
    def detect(self, text: str) -> tuple[float, list[str]]:
        """Detect prompt injection patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (score, reasons)
            - score: 0.0 to 1.0, higher = more suspicious
            - reasons: List of matched rule descriptions
        """
        max_score = 0.0
        reasons = []
        
        for pattern, score in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                max_score = max(max_score, score)
                reasons.append(f"rule_match:{pattern.pattern[:50]}")
        
        return max_score, reasons
    
    def has_suspicious_encoding(self, text: str) -> tuple[bool, Optional[str]]:
        """Check for suspicious encoding/obfuscation.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (is_suspicious, reason)
        """
        # Check for zero-width characters
        zero_width_chars = [
            "\u200b",  # Zero width space
            "\u200c",  # Zero width non-joiner
            "\u200d",  # Zero width joiner
            "\ufeff",  # Zero width no-break space
        ]
        
        for char in zero_width_chars:
            if char in text:
                return True, "zero_width_chars"
        
        # Check for excessive Unicode variation selectors
        if text.count("\ufe0f") > 5:
            return True, "excessive_variation_selectors"
        
        # Check for homoglyph attempts (Cyrillic/Greek that look like Latin)
        suspicious_chars = ["а", "е", "о", "р", "с", "х", "А", "Е", "О", "Р", "С", "Х"]
        if any(char in text for char in suspicious_chars):
            if re.search(r"[a-zA-Z]", text):  # Mix of Latin and lookalikes
                return True, "homoglyph_mix"
        
        return False, None
    
    def check_base64_like(self, text: str) -> bool:
        """Check if text contains base64-like strings.
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious base64 found
        """
        # Look for long base64-like strings
        base64_pattern = r"[A-Za-z0-9+/]{30,}={0,2}"
        matches = re.findall(base64_pattern, text)
        
        return len(matches) > 0
