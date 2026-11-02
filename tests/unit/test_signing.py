"""Tests for cryptographic signing."""
import pytest
from decimal import Decimal
import time

from cleanroom.crypto.keys import KeyStore
from cleanroom.crypto.signing import sign_mandate, verify_mandate
from cleanroom.models.contracts import Mandate, Intent, Money, Address


def test_keypair_generation():
    """Test Ed25519 keypair generation."""
    store = KeyStore("data/test_keys")
    private_key, public_key = store.generate_keypair()
    
    assert private_key is not None
    assert public_key is not None


def test_mandate_signing():
    """Test mandate signing and verification."""
    # Generate keys
    store = KeyStore("data/test_keys")
    private_key, public_key = store.ensure_keypair()
    
    # Create mandate
    mandate = Mandate(
        id="mandate_001",
        user_id="user_001",
        issued_at=time.time(),
        expires_at=time.time() + 3600,
        intent=Intent(
            text="Buy a USB-C charger",
            category="chargers",
            required_features=["usb-c", "fast-charging"],
        ),
        allowed_payees=["merchant_legit_electronics"],
        max_total=Money(currency="USD", value=Decimal("50.00")),
        max_qty_per_item=2,
        max_line_items=1,
        ship_to=Address(
            full_name="Test User",
            line1="123 Test St",
            city="San Francisco",
            region="CA",
            postal_code="94102",
        ),
        step_up_over=Money(currency="USD", value=Decimal("30.00")),
        nonce="nonce_001",
    )
    
    # Sign
    signature = sign_mandate(mandate, private_key)
    assert signature
    assert len(signature) > 0
    
    mandate.signature = signature
    
    # Verify
    assert verify_mandate(mandate, public_key)
    
    # Tamper with mandate
    mandate.max_total.value = Decimal("100.00")
    assert not verify_mandate(mandate, public_key)


def test_signature_determinism():
    """Test that signing is deterministic."""
    store = KeyStore("data/test_keys")
    private_key, public_key = store.ensure_keypair()
    
    mandate = Mandate(
        id="mandate_002",
        user_id="user_001",
        issued_at=1699000000.0,
        expires_at=1699003600.0,
        intent=Intent(text="Test", category="test"),
        allowed_payees=["merchant_001"],
        max_total=Money(currency="USD", value=Decimal("10.00")),
        ship_to=Address(
            full_name="Test",
            line1="123 St",
            city="City",
            region="ST",
            postal_code="12345",
        ),
        step_up_over=Money(currency="USD", value=Decimal("5.00")),
        nonce="nonce_002",
    )
    
    sig1 = sign_mandate(mandate, private_key)
    sig2 = sign_mandate(mandate, private_key)
    
    assert sig1 == sig2
