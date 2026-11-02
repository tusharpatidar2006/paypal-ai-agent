"""Policy checks for mandate enforcement."""
import time
from typing import Optional
from decimal import Decimal

from cleanroom.models.contracts import (
    Mandate,
    OrderDraft,
    PinnedSnapshot,
    Money,
    Verdict,
)
from cleanroom.policy import reasons


def check_mandate_signature(
    mandate: Mandate,
    verify_fn: callable,
) -> Optional[str]:
    """Check mandate signature validity.
    
    Args:
        mandate: Mandate to check
        verify_fn: Function to verify signature
        
    Returns:
        Reason code if invalid, None if valid
    """
    if not mandate.signature:
        return reasons.SIG_INVALID
    
    if not verify_fn(mandate):
        return reasons.SIG_INVALID
    
    return None


def check_mandate_expiry(mandate: Mandate) -> Optional[str]:
    """Check if mandate has expired.
    
    Args:
        mandate: Mandate to check
        
    Returns:
        Reason code if expired, None if valid
    """
    now = time.time()
    if now > mandate.expires_at:
        return reasons.MANDATE_EXPIRED
    return None


def check_nonce(
    mandate: Mandate,
    nonce_store: any,
) -> Optional[str]:
    """Check nonce for replay attack prevention.
    
    Args:
        mandate: Mandate to check
        nonce_store: NonceStore instance
        
    Returns:
        Reason code if replay detected, None if valid
    """
    if mandate.single_use:
        if not nonce_store.check_and_mark(mandate.id, mandate.nonce):
            return reasons.MANDATE_REPLAY
    return None


def check_snapshot_validity(
    snapshot: PinnedSnapshot,
    session_id: str,
    hmac_verify_fn: callable,
) -> Optional[str]:
    """Check pinned snapshot validity.
    
    Args:
        snapshot: Snapshot to check
        session_id: Expected session ID
        hmac_verify_fn: Function to verify HMAC
        
    Returns:
        Reason code if invalid, None if valid
    """
    # Check session ID
    if snapshot.session_id != session_id:
        return reasons.SNAPSHOT_INVALID
    
    # Check TTL
    now = time.time()
    if now > snapshot.captured_at + snapshot.ttl_s:
        return reasons.SNAPSHOT_INVALID
    
    # Verify HMAC
    if not hmac_verify_fn(snapshot):
        return reasons.SNAPSHOT_INVALID
    
    return None


def check_payee(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check if payee is in allowed list.
    
    Args:
        order: Order draft
        mandate: Mandate with allowed payees
        
    Returns:
        Reason code if not allowed, None if valid
    """
    if order.payee_merchant_id not in mandate.allowed_payees:
        return reasons.PAYEE_NOT_ALLOWED
    return None


def check_currency(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check if currency matches mandate.
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if mismatch, None if valid
    """
    if order.total.currency != mandate.max_total.currency:
        return reasons.CURRENCY_MISMATCH
    return None


def check_shipping_address(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check if shipping address matches mandate.
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if mismatch, None if valid
    """
    if order.ship_to.model_dump() != mandate.ship_to.model_dump():
        return reasons.SHIPTO_MISMATCH
    return None


def check_total_cap(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check if total is within mandate cap.
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if over cap, None if valid
    """
    if order.total > mandate.max_total:
        return reasons.TOTAL_OVER_CAP
    return None


def check_quantity_limits(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check quantity limits (soft check -> CHALLENGE).
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if over limit, None if valid
    """
    for line in order.lines:
        if line.get("qty", 0) > mandate.max_qty_per_item:
            return reasons.QTY_OVER_LIMIT
    return None


def check_line_items_limit(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check number of line items (soft check -> CHALLENGE).
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if over limit, None if valid
    """
    if len(order.lines) > mandate.max_line_items:
        return reasons.LINE_ITEMS_OVER_LIMIT
    return None


def check_skus_viewed(
    order: OrderDraft,
    snapshot: PinnedSnapshot,
) -> Optional[str]:
    """Check if all SKUs were viewed (soft check -> CHALLENGE).
    
    Args:
        order: Order draft
        snapshot: Pinned snapshot
        
    Returns:
        Reason code if SKU not viewed, None if valid
    """
    for line in order.lines:
        sku = line.get("sku")
        if sku not in snapshot.items:
            return reasons.SKU_NOT_VIEWED
    return None


def check_category_match(
    order: OrderDraft,
    snapshot: PinnedSnapshot,
    mandate: Mandate,
) -> Optional[str]:
    """Check if item categories match mandate intent (soft check).
    
    Args:
        order: Order draft
        snapshot: Pinned snapshot
        mandate: Mandate with intent
        
    Returns:
        Reason code if mismatch, None if valid
    """
    intent_category = mandate.intent.category.lower()
    
    for line in order.lines:
        sku = line.get("sku")
        if sku in snapshot.items:
            item_category = snapshot.items[sku].category.lower()
            if item_category != intent_category:
                return reasons.CATEGORY_MISMATCH
    
    return None


def check_step_up_threshold(
    order: OrderDraft,
    mandate: Mandate,
) -> Optional[str]:
    """Check if total exceeds step-up threshold (soft check).
    
    Args:
        order: Order draft
        mandate: Mandate
        
    Returns:
        Reason code if over threshold, None if valid
    """
    if order.total > mandate.step_up_over:
        return reasons.OVER_STEP_UP
    return None


def check_price_drift(
    order: OrderDraft,
    snapshot: PinnedSnapshot,
    tolerance_percent: float = 5.0,
) -> Optional[str]:
    """Check for price drift from snapshot (soft check).
    
    Args:
        order: Order draft
        snapshot: Pinned snapshot
        tolerance_percent: Allowed drift percentage
        
    Returns:
        Reason code if drift detected, None if valid
    """
    for line in order.lines:
        sku = line.get("sku")
        order_price = Decimal(str(line.get("unit_price", {}).get("value", 0)))
        
        if sku in snapshot.items:
            snapshot_price = snapshot.items[sku].unit_price.value
            diff_percent = abs(
                (order_price - snapshot_price) / snapshot_price * 100
            )
            
            if diff_percent > tolerance_percent:
                return reasons.PRICE_DRIFT
    
    return None
