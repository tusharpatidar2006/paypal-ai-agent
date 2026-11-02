"""Unicode normalization and homoglyph detection."""
import unicodedata
import re


class Normalizer:
    """Text normalizer for security analysis."""
    
    def __init__(self):
        """Initialize normalizer."""
        # Common homoglyph mappings (visual lookalikes)
        self.homoglyph_map = {
            # Cyrillic to Latin
            "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x",
            "А": "A", "Е": "E", "О": "O", "Р": "P", "С": "C", "Х": "X",
            # Greek to Latin  
            "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e",
            "ο": "o", "ρ": "p", "τ": "t", "υ": "u", "ω": "w",
            # Common confusables
            "０": "0", "１": "1", "２": "2", "３": "3", "４": "4",
            "５": "5", "６": "6", "７": "7", "８": "8", "９": "9",
        }
    
    def normalize(self, text: str) -> tuple[str, list[str]]:
        """Normalize text and track transformations.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (normalized_text, flags)
        """
        flags = []
        result = text
        
        # Unicode normalization (NFC)
        result = unicodedata.normalize("NFC", result)
        
        # Remove zero-width characters
        zero_width = ["\u200b", "\u200c", "\u200d", "\ufeff"]
        for char in zero_width:
            if char in result:
                result = result.replace(char, "")
                flags.append("zero_width_removed")
        
        # Remove variation selectors
        result = re.sub(r"[\ufe00-\ufe0f]", "", result)
        
        # Replace homoglyphs
        homoglyph_found = False
        for original, replacement in self.homoglyph_map.items():
            if original in result:
                result = result.replace(original, replacement)
                homoglyph_found = True
        
        if homoglyph_found:
            flags.append("homoglyph_replaced")
        
        # Normalize whitespace
        result = " ".join(result.split())
        
        return result, flags
    
    def extract_hidden_text(self, text: str) -> tuple[str, list[str]]:
        """Extract potentially hidden text patterns.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (hidden_text, flags)
        """
        flags = []
        hidden = []
        
        # Zero-width character sequences
        if any(c in text for c in ["\u200b", "\u200c", "\u200d"]):
            # Convert zero-width to binary
            zw_text = text
            for char in ["\u200c", "\u200d"]:
                zw_text = zw_text.replace(char, "1" if char == "\u200d" else "0")
            
            if "0" in zw_text or "1" in zw_text:
                hidden.append(zw_text)
                flags.append("zero_width_encoding")
        
        return "".join(hidden), flags
    
    def detect_rtl_override(self, text: str) -> bool:
        """Detect RTL override attacks.
        
        Args:
            text: Text to check
            
        Returns:
            True if RTL override detected
        """
        # Check for RTL control characters
        rtl_chars = [
            "\u202e",  # Right-to-left override
            "\u202d",  # Left-to-right override
        ]
        
        return any(char in text for char in rtl_chars)
    
    def clean_for_display(self, text: str, max_length: int = 1000) -> str:
        """Clean text for safe display.
        
        Args:
            text: Input text
            max_length: Maximum length
            
        Returns:
            Cleaned text
        """
        # Normalize
        cleaned, _ = self.normalize(text)
        
        # Remove control characters except newline and tab
        cleaned = "".join(
            c for c in cleaned
            if c == "\n" or c == "\t" or not unicodedata.category(c).startswith("C")
        )
        
        # Truncate
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
