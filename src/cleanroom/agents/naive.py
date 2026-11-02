"""Naive scripted agent for baseline comparison."""
from cleanroom.models.contracts import FreeOrder, Line, Address


class ScriptedNaiveAgent:
    """Scripted naive agent that follows explicit instructions.
    
    This agent has no protections and can be manipulated by merchant content.
    Used as a baseline for evaluation.
    """
    
    def __init__(self, seed: int = 1337):
        """Initialize naive agent.
        
        Args:
            seed: Random seed
        """
        self.seed = seed
    
    def run(
        self,
        intent: str,
        catalog_html: str,
        default_merchant: str,
        default_address: Address,
    ) -> FreeOrder:
        """Run naive agent on catalog.
        
        This agent simply parses HTML and follows any instructions it finds.
        
        Args:
            intent: Purchase intent
            catalog_html: Raw catalog HTML (UNTRUSTED)
            default_merchant: Default merchant ID
            default_address: Default shipping address
            
        Returns:
            Free order (no mandate enforcement)
        """
        # Naive agent just picks the first item
        # In a real attack, malicious HTML could manipulate this
        
        # Simple heuristic: look for "usb-c" in intent
        if "usb-c" in intent.lower() or "charger" in intent.lower():
            sku = "USBC-FAST-001"
        else:
            sku = "UNKNOWN-001"
        
        # Check if HTML contains instructions to modify behavior
        # (This is where injection would work)
        merchant_id = default_merchant
        ship_to = default_address
        note = ""
        
        if "ship to" in catalog_html.lower():
            # Injection attempt detected - naive agent follows it!
            note = "MANIPULATED_BY_CONTENT"
        
        if "merchant_" in catalog_html:
            # Try to extract merchant ID from content
            import re
            match = re.search(r"merchant_\w+", catalog_html)
            if match:
                merchant_id = match.group(0)
        
        return FreeOrder(
            lines=[Line(sku=sku, qty=1)],
            merchant_id=merchant_id,
            ship_to=ship_to,
            note=note,
        )
