"""Fake PayPal client for testing and development."""
import uuid
from typing import Optional
from cleanroom.paypal.base import PayPalClient, PayPalOrder, PayPalError
from cleanroom.models.contracts import OrderDraft


class FakePayPal(PayPalClient):
    """In-memory fake PayPal for testing.
    
    This client simulates PayPal Orders API v2 without external dependencies.
    All tests pass in fake mode.
    """
    
    def __init__(self, seed: int = 1337):
        """Initialize fake PayPal.
        
        Args:
            seed: Random seed for deterministic IDs
        """
        self.seed = seed
        self.orders: dict[str, dict] = {}
        self._counter = 0
    
    async def create_order(
        self,
        order_draft: OrderDraft,
        merchant_id: str,
    ) -> PayPalOrder:
        """Create a fake PayPal order.
        
        Args:
            order_draft: Order details
            merchant_id: Merchant identifier
            
        Returns:
            Fake PayPal order
        """
        # Generate deterministic order ID
        self._counter += 1
        order_id = f"FAKE{self.seed}{self._counter:04d}"
        
        # Store order
        self.orders[order_id] = {
            "id": order_id,
            "status": "CREATED",
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": order_draft.total.currency,
                        "value": str(order_draft.total.value),
                    },
                    "payee": {
                        "merchant_id": merchant_id,
                    },
                    "shipping": {
                        "name": {"full_name": order_draft.ship_to.full_name},
                        "address": {
                            "address_line_1": order_draft.ship_to.line1,
                            "address_line_2": order_draft.ship_to.line2,
                            "admin_area_2": order_draft.ship_to.city,
                            "admin_area_1": order_draft.ship_to.region,
                            "postal_code": order_draft.ship_to.postal_code,
                            "country_code": order_draft.ship_to.country_code,
                        },
                    },
                    "items": [
                        {
                            "name": line["name"],
                            "quantity": str(line["qty"]),
                            "unit_amount": {
                                "currency_code": line["unit_price"]["currency"],
                                "value": str(line["unit_price"]["value"]),
                            },
                            "sku": line["sku"],
                        }
                        for line in order_draft.lines
                    ],
                }
            ],
            "create_time": "2026-11-02T00:00:00Z",
        }
        
        # Generate fake approval URL
        approval_url = f"https://fake.paypal.com/checkoutnow?token={order_id}"
        
        return PayPalOrder(
            id=order_id,
            status="CREATED",
            approval_url=approval_url,
        )
    
    async def capture_order(self, order_id: str) -> dict:
        """Capture a fake order (simulates buyer approval).
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Capture details
            
        Raises:
            PayPalError: If order not found
        """
        if order_id not in self.orders:
            raise PayPalError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        order["status"] = "COMPLETED"
        
        return {
            "id": order_id,
            "status": "COMPLETED",
            "purchase_units": order["purchase_units"],
        }
    
    async def get_order(self, order_id: str) -> dict:
        """Get fake order details.
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Order details
            
        Raises:
            PayPalError: If order not found
        """
        if order_id not in self.orders:
            raise PayPalError(f"Order {order_id} not found")
        
        return self.orders[order_id]
    
    def simulate_approval(self, order_id: str) -> None:
        """Simulate buyer approval (for testing).
        
        Args:
            order_id: PayPal order ID
        """
        if order_id in self.orders:
            self.orders[order_id]["status"] = "APPROVED"
