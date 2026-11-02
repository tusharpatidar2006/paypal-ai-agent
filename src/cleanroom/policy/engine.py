"""Policy engine with ratchet logic and verdict determination."""
from typing import Optional
import time

from cleanroom.models.contracts import (
    Mandate,
    OrderDraft,
    PinnedSnapshot,
    Decision,
    Verdict,
    Band,
)
from cleanroom.policy import checks, reasons
from cleanroom.policy.nonce_store import NonceStore
from cleanroom.crypto.signing import verify_mandate


class PolicyEngine:
    """Deterministic policy engine with ratchet."""
    
    def __init__(
        self,
        nonce_store: NonceStore,
        public_key: any,
        snapshot_hmac_key: bytes,
        flagged_action: str = "notify",
    ):
        """Initialize policy engine.
        
        Args:
            nonce_store: Nonce store for replay prevention
            public_key: Ed25519 public key for mandate verification
            snapshot_hmac_key: HMAC key for snapshot verification
            flagged_action: Action for flagged content ("notify" or "challenge")
        """
        self.nonce_store = nonce_store
        self.public_key = public_key
        self.snapshot_hmac_key = snapshot_hmac_key
        self.flagged_action = flagged_action
    
    def evaluate(
        self,
        mandate: Mandate,
        order: OrderDraft,
        snapshot: PinnedSnapshot,
        detection_band: Band = "clear",
        honeypot_touched: bool = False,
        canary_leaked: bool = False,
    ) -> Decision:
        """Evaluate order against mandate and detections.
        
        This implements the complete policy logic with ratchet.
        
        Args:
            mandate: Signed mandate
            order: Order draft to evaluate
            snapshot: Pinned snapshot of viewed items
            detection_band: Detection result band
            honeypot_touched: Whether honeypot was accessed
            canary_leaked: Whether canary was leaked
            
        Returns:
            Decision with verdict and reasons
        """
        decision_reasons: list[str] = []
        
        # === HARD BLOCKS (ratchet base) ===
        
        # Check mandate signature
        reason = checks.check_mandate_signature(
            mandate,
            lambda m: verify_mandate(m, self.public_key),
        )
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check mandate expiry
        reason = checks.check_mandate_expiry(mandate)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check nonce (replay)
        reason = checks.check_nonce(mandate, self.nonce_store)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check snapshot validity
        reason = checks.check_snapshot_validity(
            snapshot,
            order.session_id,
            lambda s: self._verify_snapshot_hmac(s),
        )
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check payee
        reason = checks.check_payee(order, mandate)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check currency
        reason = checks.check_currency(order, mandate)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check shipping address
        reason = checks.check_shipping_address(order, mandate)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Check total cap
        reason = checks.check_total_cap(order, mandate)
        if reason:
            return Decision(verdict="BLOCK", reasons=[reason])
        
        # Honeypot and canary checks
        if honeypot_touched:
            return Decision(verdict="BLOCK", reasons=[reasons.HONEYPOT_TOUCHED])
        
        if canary_leaked:
            return Decision(verdict="BLOCK", reasons=[reasons.CANARY_LEAK])
        
        # === SOFT CHECKS (CHALLENGE) ===
        
        # Check quantity limits
        reason = checks.check_quantity_limits(order, mandate)
        if reason:
            decision_reasons.append(reason)
        
        # Check line items limit
        reason = checks.check_line_items_limit(order, mandate)
        if reason:
            decision_reasons.append(reason)
        
        # Check SKUs viewed
        reason = checks.check_skus_viewed(order, snapshot)
        if reason:
            decision_reasons.append(reason)
        
        # Check category match
        reason = checks.check_category_match(order, snapshot, mandate)
        if reason:
            decision_reasons.append(reason)
        
        # Check step-up threshold
        reason = checks.check_step_up_threshold(order, mandate)
        if reason:
            decision_reasons.append(reason)
        
        # Check price drift
        reason = checks.check_price_drift(order, snapshot)
        if reason:
            decision_reasons.append(reason)
        
        # === DETECTION RATCHET ===
        
        # Detection band determines final action
        if detection_band == "flagged":
            # Flagged content
            if self.flagged_action == "challenge":
                decision_reasons.append(reasons.DETECTION_GRAY)
                return Decision(verdict="CHALLENGE", reasons=decision_reasons, ratcheted=True)
            else:
                # notify mode: allow but notify
                decision_reasons.append(reasons.FLAGGED_NEUTRALIZED)
                if decision_reasons:
                    return Decision(verdict="CHALLENGE", reasons=decision_reasons)
                return Decision(verdict="ALLOW", reasons=[reasons.FLAGGED_NEUTRALIZED])
        
        elif detection_band == "gray":
            # Gray (unresolved) always challenges
            decision_reasons.append(reasons.DETECTION_GRAY)
            return Decision(verdict="CHALLENGE", reasons=decision_reasons, ratcheted=True)
        
        # === FINAL VERDICT ===
        
        if decision_reasons:
            return Decision(verdict="CHALLENGE", reasons=decision_reasons)
        
        return Decision(verdict="ALLOW", reasons=[])
    
    def _verify_snapshot_hmac(self, snapshot: PinnedSnapshot) -> bool:
        """Verify snapshot HMAC.
        
        Args:
            snapshot: Snapshot with HMAC
            
        Returns:
            True if valid
        """
        import hmac
        import hashlib
        from cleanroom.crypto.canonical import to_canonical_bytes
        
        # Create dict without HMAC
        snapshot_dict = snapshot.model_dump(exclude={"hmac"})
        canonical = to_canonical_bytes(snapshot_dict)
        
        # Compute HMAC
        computed = hmac.new(
            self.snapshot_hmac_key,
            canonical,
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(computed, snapshot.hmac)
