"""
Key management for Crypto-Replicator.

Supports multiple RSA key pairs for key rotation:
- Load keys from directory
- Encrypt with current key
- Decrypt with any historical key
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .crypto import HybridDecryptor, HybridEncryptor, generate_key_pair


logger = logging.getLogger(__name__)


@dataclass
class KeyInfo:
    """Metadata about a key."""
    key_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    public_key_path: Optional[Path] = None
    private_key_path: Optional[Path] = None


@dataclass
class KeyRotationManager:
    """
    Manages multiple RSA key pairs for key rotation.
    
    Usage:
        manager = KeyRotationManager(keys_dir=Path("./keys"))
        manager.load_keys()
        
        # Encrypt with current key
        envelope = manager.encrypt(data, table="audit", operation="INSERT")
        
        # Decrypt with any key (by key_id in envelope)
        data = manager.decrypt(envelope)
    """
    
    keys_dir: Path
    current_key_id: Optional[str] = None
    keys: Dict[str, KeyInfo] = field(default_factory=dict)
    _encryptors: Dict[str, HybridEncryptor] = field(default_factory=dict)
    _decryptors: Dict[str, HybridDecryptor] = field(default_factory=dict)
    
    def load_keys(self) -> None:
        """
        Load all keys from the keys directory.
        
        Expected structure:
        keys/
        ├── key-2024-01/
        │   ├── public.pem
        │   └── private.pem  (optional, only for decryption)
        ├── key-2024-02/
        │   ├── public.pem
        │   └── private.pem
        └── current -> key-2024-02  (symlink to current)
        """
        if not self.keys_dir.exists():
            logger.warning(f"Keys directory not found: {self.keys_dir}")
            return
        
        # Find current key (symlink)
        current_link = self.keys_dir / "current"
        if current_link.is_symlink():
            self.current_key_id = current_link.resolve().name
        
        # Load all key directories
        for key_dir in self.keys_dir.iterdir():
            if not key_dir.is_dir() or key_dir.name == "current":
                continue
            
            key_id = key_dir.name
            public_path = key_dir / "public.pem"
            private_path = key_dir / "private.pem"
            
            if not public_path.exists():
                logger.warning(f"No public key in {key_dir}")
                continue
            
            # Create key info
            key_info = KeyInfo(
                key_id=key_id,
                created_at=datetime.fromtimestamp(public_path.stat().st_mtime),
                public_key_path=public_path,
                private_key_path=private_path if private_path.exists() else None,
                is_active=(key_id == self.current_key_id),
            )
            self.keys[key_id] = key_info
            
            # Load encryptor (always available)
            self._encryptors[key_id] = HybridEncryptor(
                public_key_path=public_path,
                key_id=key_id
            )
            
            # Load decryptor (if private key available)
            if private_path.exists():
                self._decryptors[key_id] = HybridDecryptor(
                    private_key_path=private_path
                )
            
            logger.info(f"Loaded key: {key_id} (active={key_info.is_active})")
        
        # If no current key set, use the most recent
        if not self.current_key_id and self.keys:
            self.current_key_id = max(
                self.keys.keys(),
                key=lambda k: self.keys[k].created_at
            )
            logger.info(f"Auto-selected current key: {self.current_key_id}")
    
    def get_current_encryptor(self) -> HybridEncryptor:
        """Get the encryptor for the current key."""
        if not self.current_key_id:
            raise ValueError("No current key set")
        return self._encryptors[self.current_key_id]
    
    def get_decryptor(self, key_id: str) -> HybridDecryptor:
        """Get the decryptor for a specific key."""
        if key_id not in self._decryptors:
            raise ValueError(f"No private key available for: {key_id}")
        return self._decryptors[key_id]
    
    def encrypt(self, data: dict, table: str, operation: str):
        """Encrypt data with the current key."""
        return self.get_current_encryptor().encrypt(
            data=data,
            table=table,
            operation=operation
        )
    
    def decrypt(self, envelope):
        """Decrypt an envelope using the appropriate key."""
        return self.get_decryptor(envelope.key_id).decrypt(envelope)
    
    def rotate_key(self, new_key_id: Optional[str] = None) -> str:
        """
        Create and activate a new key pair.
        
        Args:
            new_key_id: Optional ID for the new key (default: key-YYYY-MM)
        
        Returns:
            The new key ID
        """
        if new_key_id is None:
            new_key_id = f"key-{datetime.now().strftime('%Y-%m')}"
        
        # Generate new key pair
        private_pem, public_pem = generate_key_pair(2048)
        
        # Create directory
        key_dir = self.keys_dir / new_key_id
        key_dir.mkdir(parents=True, exist_ok=True)
        
        # Save keys
        (key_dir / "public.pem").write_bytes(public_pem)
        (key_dir / "private.pem").write_bytes(private_pem)
        
        # Update current symlink
        current_link = self.keys_dir / "current"
        if current_link.exists() or current_link.is_symlink():
            current_link.unlink()
        current_link.symlink_to(new_key_id)
        
        # Reload keys
        self.load_keys()
        
        logger.info(f"Rotated to new key: {new_key_id}")
        return new_key_id
    
    def list_keys(self) -> list:
        """List all available keys."""
        return [
            {
                "key_id": k.key_id,
                "created_at": k.created_at.isoformat(),
                "is_active": k.is_active,
                "has_private_key": k.private_key_path is not None,
            }
            for k in sorted(self.keys.values(), key=lambda x: x.created_at)
        ]
