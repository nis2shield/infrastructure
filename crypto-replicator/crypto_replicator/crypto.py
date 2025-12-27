"""
Hybrid encryption module for Crypto-Replicator.

Implements the "Digital Envelope" pattern:
- AES-256-GCM for data encryption (fast, authenticated)
- RSA-OAEP for key wrapping (asymmetric, secure key exchange)

This ensures:
- Only the holder of the RSA private key can decrypt
- Cloud storage cannot read the data (no private key)
- Each message uses a unique session key (forward secrecy)
"""

import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass
class EncryptedEnvelope:
    """
    The encrypted envelope sent to cloud storage.
    
    Contains all data needed to decrypt (except the private key).
    """
    version: str
    timestamp: str
    table: str
    operation: str  # INSERT, UPDATE, DELETE
    encrypted_data: str  # Base64 encoded
    encrypted_key: str   # Base64 encoded (RSA wrapped AES key)
    iv: str              # Base64 encoded (12 bytes for GCM)
    tag: str             # Base64 encoded (16 bytes GCM auth tag)
    key_id: str          # Which RSA key was used
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps({
            "version": self.version,
            "timestamp": self.timestamp,
            "table": self.table,
            "operation": self.operation,
            "encrypted_data": self.encrypted_data,
            "encrypted_key": self.encrypted_key,
            "iv": self.iv,
            "tag": self.tag,
            "key_id": self.key_id,
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "EncryptedEnvelope":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


class HybridEncryptor:
    """
    Implements hybrid encryption using AES-256-GCM + RSA-OAEP.
    
    Usage:
        encryptor = HybridEncryptor(public_key_path="/keys/cloud.pub")
        envelope = encryptor.encrypt(data, table="users", operation="INSERT")
        # Send envelope.to_json() to cloud
    """
    
    VERSION = "1.0"
    AES_KEY_SIZE = 32  # 256 bits
    IV_SIZE = 12       # 96 bits for GCM
    
    def __init__(
        self,
        public_key_path: Optional[Path] = None,
        public_key_pem: Optional[bytes] = None,
        key_id: str = "default"
    ):
        """
        Initialize with RSA public key.
        
        Args:
            public_key_path: Path to PEM-encoded RSA public key file
            public_key_pem: PEM-encoded RSA public key bytes
            key_id: Identifier for the key (for key rotation)
        """
        self.key_id = key_id
        
        if public_key_pem:
            self._public_key = serialization.load_pem_public_key(public_key_pem)
        elif public_key_path:
            with open(public_key_path, "rb") as f:
                self._public_key = serialization.load_pem_public_key(f.read())
        else:
            raise ValueError("Must provide public_key_path or public_key_pem")
    
    def encrypt(
        self,
        data: dict,
        table: str,
        operation: str,
        timestamp: Optional[datetime] = None
    ) -> EncryptedEnvelope:
        """
        Encrypt data using hybrid encryption.
        
        Args:
            data: Dictionary to encrypt
            table: Database table name
            operation: INSERT, UPDATE, or DELETE
            timestamp: Optional timestamp (defaults to now)
        
        Returns:
            EncryptedEnvelope ready to send to cloud
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        # Serialize data to JSON bytes
        plaintext = json.dumps(data, default=str).encode("utf-8")
        
        # Generate random AES session key
        session_key = os.urandom(self.AES_KEY_SIZE)
        
        # Generate random IV for GCM
        iv = os.urandom(self.IV_SIZE)
        
        # Encrypt data with AES-256-GCM
        aesgcm = AESGCM(session_key)
        # GCM produces ciphertext + tag concatenated
        ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
        
        # Split ciphertext and tag (last 16 bytes is tag)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        # Wrap session key with RSA-OAEP
        encrypted_key = self._public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptedEnvelope(
            version=self.VERSION,
            timestamp=timestamp.isoformat(),
            table=table,
            operation=operation,
            encrypted_data=base64.b64encode(ciphertext).decode("ascii"),
            encrypted_key=base64.b64encode(encrypted_key).decode("ascii"),
            iv=base64.b64encode(iv).decode("ascii"),
            tag=base64.b64encode(tag).decode("ascii"),
            key_id=self.key_id,
        )


class HybridDecryptor:
    """
    Decrypts envelopes using RSA private key.
    
    This is used for disaster recovery - NOT deployed to cloud.
    The private key should be kept secure (offline/HSM).
    """
    
    def __init__(
        self,
        private_key_path: Optional[Path] = None,
        private_key_pem: Optional[bytes] = None,
        private_key_password: Optional[bytes] = None
    ):
        """
        Initialize with RSA private key.
        
        Args:
            private_key_path: Path to PEM-encoded RSA private key file
            private_key_pem: PEM-encoded RSA private key bytes
            private_key_password: Password if key is encrypted
        """
        if private_key_pem:
            self._private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=private_key_password
            )
        elif private_key_path:
            with open(private_key_path, "rb") as f:
                self._private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=private_key_password
                )
        else:
            raise ValueError("Must provide private_key_path or private_key_pem")
    
    def decrypt(self, envelope: EncryptedEnvelope) -> dict:
        """
        Decrypt an envelope.
        
        Args:
            envelope: The encrypted envelope to decrypt
        
        Returns:
            Original data dictionary
        """
        # Decode base64
        ciphertext = base64.b64decode(envelope.encrypted_data)
        encrypted_key = base64.b64decode(envelope.encrypted_key)
        iv = base64.b64decode(envelope.iv)
        tag = base64.b64decode(envelope.tag)
        
        # Unwrap session key with RSA-OAEP
        session_key = self._private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data with AES-256-GCM
        aesgcm = AESGCM(session_key)
        # Reconstruct ciphertext + tag for decryption
        ciphertext_with_tag = ciphertext + tag
        plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)
        
        # Parse JSON
        return json.loads(plaintext.decode("utf-8"))


def generate_key_pair(
    key_size: int = 2048
) -> tuple[bytes, bytes]:
    """
    Generate a new RSA key pair.
    
    Args:
        key_size: RSA key size in bits (2048 or 4096 recommended)
    
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem
