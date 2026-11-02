"""PayPal client interface."""
from abc import ABC, abstractmethod
from typing import Optional
from cleanroom.models.contracts import OrderDraft, Money, Address


class PayPalOrder:
    """PayPal order response."""
    
    def __init__(
        self,
        id: str,
        status: str,
        approval_url: Optional[str] = None,
    ):
        """Initialize PayPal order.
        
        Args:
            id: PayPal order ID
            status: Order status
            approval_url: URL for buyer approval
        """
        self.id = id
        self.status = status
        self.approval_url = approval_url


class PayPalClient(ABC):
    """Abstract PayPal client interface."""
    
    @abstractmethod
    async def create_order(
        self,
        order_draft: OrderDraft,
        merchant_id: str,
    ) -> PayPalOrder:
        """Create a PayPal order.
        
        Args:
            order_draft: Order details
            merchant_id: Merchant identifier
            
        Returns:
            PayPal order with ID and approval URL
            
        Raises:
            PayPalError: If order creation fails
        """
        pass
    
    @abstractmethod
    async def capture_order(self, order_id: str) -> dict:
        """Capture a PayPal order.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Capture details
            
        Raises:
            PayPalError: If capture fails
        """
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str) -> dict:
        """Get order details.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Order details
            
        Raises:
            PayPalError: If retrieval fails
        """
        pass


class PayPalError(Exception):
    """PayPal operation error."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize error.
        
        Args:
            message: Error message
            details: Optional error details
        """
        super().__init__(message)
        self.details = details or {}
