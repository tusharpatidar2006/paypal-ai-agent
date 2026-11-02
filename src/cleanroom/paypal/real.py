"""Real PayPal sandbox client using Orders API v2."""
import httpx
from typing import Optional
from cleanroom.paypal.base import PayPalClient, PayPalOrder, PayPalError
from cleanroom.paypal.mapping import to_paypal_order_request
from cleanroom.models.contracts import OrderDraft


class RealPayPal(PayPalClient):
    """Real PayPal sandbox client using httpx and Orders API v2."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api-m.sandbox.paypal.com",
        return_url: str = "http://localhost:8000/paypal/return",
        cancel_url: str = "http://localhost:8000/paypal/cancel",
    ):
        """Initialize real PayPal client.
        
        Args:
            client_id: PayPal client ID
            client_secret: PayPal client secret
            base_url: PayPal API base URL (must be sandbox)
            return_url: Return URL after approval
            cancel_url: Cancel URL
            
        Raises:
            ValueError: If base URL is not sandbox
        """
        if "sandbox" not in base_url.lower():
            raise ValueError(
                f"Real PayPal requires sandbox URL. Got: {base_url}"
            )
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.return_url = return_url
        self.cancel_url = cancel_url
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0
    
    async def _get_access_token(self) -> str:
        """Get OAuth access token.
        
        Returns:
            Access token
            
        Raises:
            PayPalError: If authentication fails
        """
        import time
        
        # Check if cached token is still valid
        if self._access_token and time.time() < self._token_expiry - 60:
            return self._access_token
        
        # Request new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise PayPalError(
                    "Failed to get access token",
                    {"status": response.status_code, "body": response.text},
                )
            
            data = response.json()
            self._access_token = data["access_token"]
            self._token_expiry = time.time() + data.get("expires_in", 3600)
            return self._access_token
    
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
            PayPal order
            
        Raises:
            PayPalError: If order creation fails
        """
        token = await self._get_access_token()
        
        # Build request
        request_body = to_paypal_order_request(
            order_draft,
            merchant_id,
            self.return_url,
            self.cancel_url,
        )
        
        # Create order
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                json=request_body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            
            if response.status_code not in (200, 201):
                raise PayPalError(
                    f"Failed to create order: {response.status_code}",
                    {"status": response.status_code, "body": response.text},
                )
            
            data = response.json()
            
            # Extract approval URL
            approval_url = None
            for link in data.get("links", []):
                if link.get("rel") == "approve":
                    approval_url = link.get("href")
                    break
            
            return PayPalOrder(
                id=data["id"],
                status=data["status"],
                approval_url=approval_url,
            )
    
    async def capture_order(self, order_id: str) -> dict:
        """Capture a PayPal order.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Capture details
            
        Raises:
            PayPalError: If capture fails
        """
        token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            
            if response.status_code not in (200, 201):
                raise PayPalError(
                    f"Failed to capture order: {response.status_code}",
                    {"status": response.status_code, "body": response.text},
                )
            
            return response.json()
    
    async def get_order(self, order_id: str) -> dict:
        """Get order details.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Order details
            
        Raises:
            PayPalError: If retrieval fails
        """
        token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/checkout/orders/{order_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise PayPalError(
                    f"Failed to get order: {response.status_code}",
                    {"status": response.status_code, "body": response.text},
                )
            
            return response.json()
