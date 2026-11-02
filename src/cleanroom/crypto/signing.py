"""Ed25519 signing and verification for mandates."""
import base64
from typing import Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

from cleanroom.crypto.canonical import to_canonical_bytes
from cleanroom.models.contracts import Mandate


def sign_mandate(mandate: Mandate, private_key: Ed25519PrivateKey) -> str:
    """Sign a mandate with Ed25519.
    
    The signature is computed over the canonical JSON of the mandate
    with the signature field removed.
    
    Args:
        mandate: Mandate to sign
        private_key: Ed25519 private key
        
    Returns:
        Base64-encoded signature
    """
    # Create dict without signature field
    mandate_dict = mandate.model_dump(mode="json", exclude={"signature"})
    
    # Convert to canonical bytes
    canonical = to_canonical_bytes(mandate_dict)
    
    # Sign
    signature_bytes = private_key.sign(canonical)
    
    # Encode to base64
    return base64.b64encode(signature_bytes).decode("ascii")


def verify_mandate(mandate: Mandate, public_key: Ed25519PublicKey) -> bool:
    """Verify a mandate signature.
    
    Args:
        mandate: Mandate with signature
        public_key: Ed25519 public key
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not mandate.signature:
        return False
    
    try:
        # Decode signature
        signature_bytes = base64.b64decode(mandate.signature)
        
        # Create dict without signature field
        mandate_dict = mandate.model_dump(mode="json", exclude={"signature"})
        
        # Convert to canonical bytes
        canonical = to_canonical_bytes(mandate_dict)
        
        # Verify
        public_key.verify(signature_bytes, canonical)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


def sign_object(obj: Any, private_key: Ed25519PrivateKey) -> str:
    """Sign any JSON-serializable object.
    
    Args:
        obj: Object to sign
        private_key: Ed25519 private key
        
    Returns:
        Base64-encoded signature
    """
    canonical = to_canonical_bytes(obj)
    signature_bytes = private_key.sign(canonical)
    return base64.b64encode(signature_bytes).decode("ascii")


def verify_object(
    obj: Any,
    signature: str,
    public_key: Ed25519PublicKey,
) -> bool:
    """Verify a signature on any object.
    
    Args:
        obj: Object that was signed
        signature: Base64-encoded signature
        public_key: Ed25519 public key
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        signature_bytes = base64.b64decode(signature)
        canonical = to_canonical_bytes(obj)
        public_key.verify(signature_bytes, canonical)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False
