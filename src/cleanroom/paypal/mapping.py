"""Map internal order drafts to PayPal Orders API v2 format."""
from cleanroom.models.contracts import OrderDraft, Money, Address


def to_paypal_amount(money: Money) -> dict:
    """Convert Money to PayPal amount.
    
    Args:
        money: Money value
        
    Returns:
        PayPal amount dict
    """
    return {
        "currency_code": money.currency,
        "value": str(money.value),
    }


def to_paypal_address(address: Address) -> dict:
    """Convert Address to PayPal shipping address.
    
    Args:
        address: Shipping address
        
    Returns:
        PayPal address dict
    """
    result = {
        "address_line_1": address.line1,
        "admin_area_2": address.city,
        "admin_area_1": address.region,
        "postal_code": address.postal_code,
        "country_code": address.country_code,
    }
    
    if address.line2:
        result["address_line_2"] = address.line2
    
    return result


def to_paypal_order_request(
    order_draft: OrderDraft,
    merchant_id: str,
    return_url: str,
    cancel_url: str,
) -> dict:
    """Convert OrderDraft to PayPal Create Order request.
    
    Args:
        order_draft: Internal order draft
        merchant_id: PayPal merchant ID
        return_url: Return URL after approval
        cancel_url: Cancel URL
        
    Returns:
        PayPal Orders v2 create request body
    """
    # Build items
    items = []
    for line in order_draft.lines:
        items.append({
            "name": line["name"],
            "quantity": str(line["qty"]),
            "unit_amount": {
                "currency_code": line["unit_price"]["currency"],
                "value": str(line["unit_price"]["value"]),
            },
            "sku": line["sku"],
        })
    
    # Build purchase unit
    purchase_unit = {
        "amount": {
            "currency_code": order_draft.total.currency,
            "value": str(order_draft.total.value),
            "breakdown": {
                "item_total": {
                    "currency_code": order_draft.total.currency,
                    "value": str(order_draft.total.value),
                },
            },
        },
        "items": items,
        "shipping": {
            "name": {
                "full_name": order_draft.ship_to.full_name,
            },
            "address": to_paypal_address(order_draft.ship_to),
        },
    }
    
    # Add payee if merchant ID provided
    if merchant_id:
        purchase_unit["payee"] = {
            "merchant_id": merchant_id,
        }
    
    # Build full request
    return {
        "intent": "CAPTURE",
        "purchase_units": [purchase_unit],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "shipping_preference": "SET_PROVIDED_ADDRESS",
            "user_action": "PAY_NOW",
        },
    }
