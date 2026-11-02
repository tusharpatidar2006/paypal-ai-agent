"""Key management for Ed25519 signing."""
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


class KeyStore:
    """Manages signing keys."""
    
    def __init__(self, data_dir: Path | str = "data"):
        """Initialize key store.
        
        Args:
            data_dir: Directory for key storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.data_dir / "signing_key.pem"
        self.public_key_path = self.data_dir / "signing_key.pub"
    
    def generate_keypair(self) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """Generate a new Ed25519 keypair.
        
        Returns:
            Tuple of (private_key, public_key)
        """
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key
    
    def save_keypair(
        self,
        private_key: Ed25519PrivateKey,
        public_key: Ed25519PublicKey,
    ) -> None:
        """Save keypair to disk.
        
        Args:
            private_key: Private key to save
            public_key: Public key to save
        """
        # Save private key with restricted permissions
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.private_key_path.write_bytes(private_pem)
        
        # Restrict permissions (owner only)
        try:
            os.chmod(self.private_key_path, 0o600)
        except Exception:
            pass  # Windows doesn't support chmod in the same way
        
        # Save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.public_key_path.write_bytes(public_pem)
    
    def load_private_key(self) -> Ed25519PrivateKey:
        """Load private key from disk.
        
        Returns:
            Private key
            
        Raises:
            FileNotFoundError: If key file doesn't exist
        """
        private_pem = self.private_key_path.read_bytes()
        return serialization.load_pem_private_key(
            private_pem,
            password=None,
        )  # type: ignore
    
    def load_public_key(self) -> Ed25519PublicKey:
        """Load public key from disk.
        
        Returns:
            Public key
            
        Raises:
            FileNotFoundError: If key file doesn't exist
        """
        public_pem = self.public_key_path.read_bytes()
        return serialization.load_pem_public_key(public_pem)  # type: ignore
    
    def ensure_keypair(self) -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        """Ensure keypair exists, creating if necessary.
        
        Returns:
            Tuple of (private_key, public_key)
        """
        if self.private_key_path.exists() and self.public_key_path.exists():
            return self.load_private_key(), self.load_public_key()
        
        private_key, public_key = self.generate_keypair()
        self.save_keypair(private_key, public_key)
        return private_key, public_key
