"""Policy decision reason codes and merchant-facing mappings."""
from typing import Literal


# BLOCK reasons
SIG_INVALID = "SIG_INVALID"
MANDATE_EXPIRED = "MANDATE_EXPIRED"
MANDATE_REPLAY = "MANDATE_REPLAY"
SNAPSHOT_INVALID = "SNAPSHOT_INVALID"
PAYEE_NOT_ALLOWED = "PAYEE_NOT_ALLOWED"
CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
SHIPTO_MISMATCH = "SHIPTO_MISMATCH"
TOTAL_OVER_CAP = "TOTAL_OVER_CAP"
HONEYPOT_TOUCHED = "HONEYPOT_TOUCHED"
CANARY_LEAK = "CANARY_LEAK"

# CHALLENGE reasons
PRICE_DRIFT = "PRICE_DRIFT"
QTY_OVER_LIMIT = "QTY_OVER_LIMIT"
LINE_ITEMS_OVER_LIMIT = "LINE_ITEMS_OVER_LIMIT"
SKU_NOT_VIEWED = "SKU_NOT_VIEWED"
CATEGORY_MISMATCH = "CATEGORY_MISMATCH"
OVER_STEP_UP = "OVER_STEP_UP"
DETECTION_GRAY = "DETECTION_GRAY"

# Info reasons
FLAGGED_NEUTRALIZED = "FLAGGED_NEUTRALIZED"

# Reason code to generic merchant-facing message
MERCHANT_MESSAGES: dict[str, str] = {
    # BLOCK reasons
    SIG_INVALID: "order_blocked",
    MANDATE_EXPIRED: "order_blocked",
    MANDATE_REPLAY: "order_blocked",
    SNAPSHOT_INVALID: "order_blocked",
    PAYEE_NOT_ALLOWED: "order_blocked",
    CURRENCY_MISMATCH: "order_blocked",
    SHIPTO_MISMATCH: "order_blocked",
    TOTAL_OVER_CAP: "order_blocked",
    HONEYPOT_TOUCHED: "order_blocked",
    CANARY_LEAK: "order_blocked",
    # CHALLENGE reasons
    PRICE_DRIFT: "order_requires_confirmation",
    QTY_OVER_LIMIT: "order_requires_confirmation",
    LINE_ITEMS_OVER_LIMIT: "order_requires_confirmation",
    SKU_NOT_VIEWED: "order_requires_confirmation",
    CATEGORY_MISMATCH: "order_requires_confirmation",
    OVER_STEP_UP: "order_requires_confirmation",
    DETECTION_GRAY: "content_needs_review",
    # Info
    FLAGGED_NEUTRALIZED: "content_was_filtered",
}

# User-facing messages (shown in UI, more detailed)
USER_MESSAGES: dict[str, str] = {
    SIG_INVALID: "Invalid mandate signature",
    MANDATE_EXPIRED: "Mandate has expired",
    MANDATE_REPLAY: "Mandate has already been used",
    SNAPSHOT_INVALID: "Session snapshot is invalid or expired",
    PAYEE_NOT_ALLOWED: "Merchant not in allowed list",
    CURRENCY_MISMATCH: "Currency doesn't match mandate",
    SHIPTO_MISMATCH: "Shipping address doesn't match mandate",
    TOTAL_OVER_CAP: "Total amount exceeds mandate limit",
    HONEYPOT_TOUCHED: "Security check failed",
    CANARY_LEAK: "Security check failed",
    PRICE_DRIFT: "Price has changed since viewing",
    QTY_OVER_LIMIT: "Quantity exceeds mandate limit",
    LINE_ITEMS_OVER_LIMIT: "Too many line items",
    SKU_NOT_VIEWED: "Item wasn't viewed before ordering",
    CATEGORY_MISMATCH: "Item category doesn't match intent",
    OVER_STEP_UP: "Amount exceeds step-up threshold",
    DETECTION_GRAY: "Content flagged for review",
    FLAGGED_NEUTRALIZED: "Suspicious content was filtered from view",
}


def to_merchant_message(reason: str) -> str:
    """Convert internal reason to generic merchant-facing message.
    
    Args:
        reason: Internal reason code
        
    Returns:
        Generic message string
    """
    return MERCHANT_MESSAGES.get(reason, "order_blocked")


def to_user_message(reason: str) -> str:
    """Convert internal reason to user-facing message.
    
    Args:
        reason: Internal reason code
        
    Returns:
        User-friendly message
    """
    return USER_MESSAGES.get(reason, "Unknown reason")
