"""
Unit tests for the crypto module.

Tests hybrid encryption (AES-256-GCM + RSA-OAEP).
"""

import json
import pytest

from crypto_replicator.crypto import (
    EncryptedEnvelope,
    HybridDecryptor,
    HybridEncryptor,
    generate_key_pair,
)


class TestGenerateKeyPair:
    """Tests for RSA key pair generation."""
    
    def test_generates_valid_pem_keys(self):
        private_pem, public_pem = generate_key_pair(2048)
        
        assert b"-----BEGIN PRIVATE KEY-----" in private_pem
        assert b"-----END PRIVATE KEY-----" in private_pem
        assert b"-----BEGIN PUBLIC KEY-----" in public_pem
        assert b"-----END PUBLIC KEY-----" in public_pem
    
    def test_keys_are_different(self):
        private_pem, public_pem = generate_key_pair(2048)
        assert private_pem != public_pem


class TestEncryptedEnvelope:
    """Tests for EncryptedEnvelope serialization."""
    
    def test_to_json_and_back(self):
        envelope = EncryptedEnvelope(
            version="1.0",
            timestamp="2024-12-27T08:00:00Z",
            table="test_table",
            operation="INSERT",
            encrypted_data="abc123",
            encrypted_key="xyz789",
            iv="iv123",
            tag="tag456",
            key_id="test-key",
        )
        
        json_str = envelope.to_json()
        restored = EncryptedEnvelope.from_json(json_str)
        
        assert restored.version == envelope.version
        assert restored.table == envelope.table
        assert restored.operation == envelope.operation
        assert restored.encrypted_data == envelope.encrypted_data


class TestHybridEncryption:
    """Tests for hybrid encryption/decryption roundtrip."""
    
    @pytest.fixture
    def key_pair(self):
        return generate_key_pair(2048)
    
    @pytest.fixture
    def encryptor(self, key_pair):
        _, public_pem = key_pair
        return HybridEncryptor(public_key_pem=public_pem, key_id="test")
    
    @pytest.fixture
    def decryptor(self, key_pair):
        private_pem, _ = key_pair
        return HybridDecryptor(private_key_pem=private_pem)
    
    def test_encrypt_decrypt_roundtrip(self, encryptor, decryptor):
        """Test that we can encrypt and decrypt data."""
        original_data = {
            "user_id": 123,
            "action": "login",
            "ip_address": "192.168.1.1",
            "sensitive": True,
        }
        
        # Encrypt
        envelope = encryptor.encrypt(
            data=original_data,
            table="audit_logs",
            operation="INSERT"
        )
        
        # Verify envelope structure
        assert envelope.version == "1.0"
        assert envelope.table == "audit_logs"
        assert envelope.operation == "INSERT"
        assert envelope.key_id == "test"
        assert len(envelope.encrypted_data) > 0
        assert len(envelope.encrypted_key) > 0
        
        # Decrypt
        decrypted_data = decryptor.decrypt(envelope)
        
        # Verify data matches
        assert decrypted_data == original_data
    
    def test_different_data_produces_different_ciphertext(self, encryptor):
        """Each encryption should produce different ciphertext (unique IV)."""
        data = {"message": "hello"}
        
        envelope1 = encryptor.encrypt(data, table="test", operation="INSERT")
        envelope2 = encryptor.encrypt(data, table="test", operation="INSERT")
        
        # Same data, but encrypted differently each time
        assert envelope1.encrypted_data != envelope2.encrypted_data
        assert envelope1.iv != envelope2.iv
    
    def test_serialize_deserialize_then_decrypt(self, encryptor, decryptor):
        """Test the full flow: encrypt -> serialize -> deserialize -> decrypt."""
        original_data = {"key": "value", "number": 42}
        
        # Encrypt and serialize
        envelope = encryptor.encrypt(data=original_data, table="t", operation="I")
        json_str = envelope.to_json()
        
        # Deserialize and decrypt
        restored_envelope = EncryptedEnvelope.from_json(json_str)
        decrypted_data = decryptor.decrypt(restored_envelope)
        
        assert decrypted_data == original_data
    
    def test_large_data(self, encryptor, decryptor):
        """Test encryption of larger data payloads."""
        large_data = {
            "items": [{"id": i, "data": "x" * 1000} for i in range(100)]
        }
        
        envelope = encryptor.encrypt(
            data=large_data,
            table="large",
            operation="INSERT"
        )
        decrypted = decryptor.decrypt(envelope)
        
        assert decrypted == large_data
    
    def test_unicode_data(self, encryptor, decryptor):
        """Test encryption of Unicode data."""
        unicode_data = {
            "message": "Ciao 🇮🇹! NIS2 è importante per la cybersecurity.",
            "emoji": "🔐🛡️💾",
        }
        
        envelope = encryptor.encrypt(
            data=unicode_data,
            table="unicode",
            operation="INSERT"
        )
        decrypted = decryptor.decrypt(envelope)
        
        assert decrypted == unicode_data


class TestSecurityProperties:
    """Tests for security properties of the encryption."""
    
    def test_wrong_private_key_fails(self):
        """Decryption with wrong key should fail."""
        # Generate two different key pairs
        _, public1 = generate_key_pair(2048)
        private2, _ = generate_key_pair(2048)
        
        encryptor = HybridEncryptor(public_key_pem=public1, key_id="key1")
        decryptor = HybridDecryptor(private_key_pem=private2)
        
        data = {"secret": "data"}
        envelope = encryptor.encrypt(data, table="t", operation="I")
        
        # Should fail to decrypt with wrong key
        with pytest.raises(Exception):
            decryptor.decrypt(envelope)
    
    def test_tampered_ciphertext_fails(self):
        """Tampered ciphertext should fail authentication."""
        private_pem, public_pem = generate_key_pair(2048)
        encryptor = HybridEncryptor(public_key_pem=public_pem, key_id="test")
        decryptor = HybridDecryptor(private_key_pem=private_pem)
        
        data = {"secret": "data"}
        envelope = encryptor.encrypt(data, table="t", operation="I")
        
        # Tamper with ciphertext
        import base64
        original = base64.b64decode(envelope.encrypted_data)
        tampered = bytes([original[0] ^ 0xFF]) + original[1:]
        envelope.encrypted_data = base64.b64encode(tampered).decode()
        
        # Should fail authentication
        with pytest.raises(Exception):
            decryptor.decrypt(envelope)
