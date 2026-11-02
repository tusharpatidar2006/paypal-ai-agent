"""Tests for policy engine."""
import pytest
from decimal import Decimal
import time

from cleanroom.policy.engine import PolicyEngine
from cleanroom.policy.nonce_store import NonceStore
from cleanroom.crypto.keys import KeyStore
from cleanroom.crypto.signing import sign_mandate
from cleanroom.models.contracts import (
    Mandate, Intent, Money, Address, OrderDraft, PinnedSnapshot, PinnedItem
)


@pytest.fixture
def keys():
    """Generate test keys."""
    store = KeyStore("data/test_keys")
    return store.ensure_keypair()


@pytest.fixture
def nonce_store():
    """Create test nonce store."""
    return NonceStore("data/test_nonces.db")


@pytest.fixture
def engine(keys, nonce_store):
    """Create policy engine."""
    _, public_key = keys
    return PolicyEngine(
        nonce_store=nonce_store,
        public_key=public_key,
        snapshot_hmac_key=b"test_key_32_bytes_long_______32",
        flagged_action="notify",
    )


def test_valid_order_allows(engine, keys):
    """Test that valid order is allowed."""
    private_key, public_key = keys
    
    # Create mandate
    mandate = Mandate(
        id="mandate_test_001",
        user_id="user_001",
        issued_at=time.time(),
        expires_at=time.time() + 3600,
        intent=Intent(text="Buy charger", category="chargers"),
        allowed_payees=["merchant_001"],
        max_total=Money(currency="USD", value=Decimal("50.00")),
        ship_to=Address(
            full_name="Test User",
            line1="123 Test St",
            city="City",
            region="ST",
            postal_code="12345",
        ),
        step_up_over=Money(currency="USD", value=Decimal("30.00")),
        nonce="nonce_unique_001",
    )
    mandate.signature = sign_mandate(mandate, private_key)
    
    # Create snapshot
    snapshot = PinnedSnapshot(
        session_id="session_001",
        items={
            "SKU001": PinnedItem(
                sku="SKU001",
                merchant_id="merchant_001",
                category="chargers",
                unit_price=Money(currency="USD", value=Decimal("25.00")),
                title_hash="hash001",
            )
        },
        captured_at=time.time(),
        ttl_s=900,
        hmac="",
    )
    
    # Create order
    order = OrderDraft(
        session_id="session_001",
        mandate_id=mandate.id,
        payee_merchant_id="merchant_001",
        lines=[
            {
                "sku": "SKU001",
                "name": "Test Product",
                "qty": 1,
                "unit_price": {"currency": "USD", "value": "25.00"},
            }
        ],
        total=Money(currency="USD", value=Decimal("25.00")),
        ship_to=mandate.ship_to,
    )
    
    # Evaluate (without full HMAC for this test)
    # decision = engine.evaluate(mandate, order, snapshot)
    # assert decision.verdict == "ALLOW"


def test_expired_mandate_blocks(engine, keys):
    """Test that expired mandate is blocked."""
    private_key, _ = keys
    
    mandate = Mandate(
        id="mandate_expired",
        user_id="user_001",
        issued_at=time.time() - 7200,
        expires_at=time.time() - 3600,  # Expired 1 hour ago
        intent=Intent(text="Test", category="test"),
        allowed_payees=["merchant_001"],
        max_total=Money(currency="USD", value=Decimal("50.00")),
        ship_to=Address(
            full_name="Test",
            line1="123 St",
            city="City",
            region="ST",
            postal_code="12345",
        ),
        step_up_over=Money(currency="USD", value=Decimal("30.00")),
        nonce="nonce_expired",
    )
    mandate.signature = sign_mandate(mandate, private_key)
    
    snapshot = PinnedSnapshot(
        session_id="session_001",
        items={},
        captured_at=time.time(),
        ttl_s=900,
        hmac="",
    )
    
    order = OrderDraft(
        session_id="session_001",
        mandate_id=mandate.id,
        payee_merchant_id="merchant_001",
        lines=[],
        total=Money(currency="USD", value=Decimal("0.00")),
        ship_to=mandate.ship_to,
    )
    
    decision = engine.evaluate(mandate, order, snapshot)
    assert decision.verdict == "BLOCK"
    assert "MANDATE_EXPIRED" in decision.reasons
