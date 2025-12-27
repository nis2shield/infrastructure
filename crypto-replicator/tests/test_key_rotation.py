"""
Tests for key rotation functionality.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from crypto_replicator.key_manager import KeyRotationManager
from crypto_replicator.crypto import generate_key_pair


class TestKeyRotationManager:
    """Tests for key rotation and multi-key management."""
    
    @pytest.fixture
    def temp_keys_dir(self):
        """Create a temporary keys directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def populated_keys_dir(self, temp_keys_dir):
        """Create a keys directory with two key pairs."""
        # Create key-2024-01
        key1_dir = temp_keys_dir / "key-2024-01"
        key1_dir.mkdir()
        private1, public1 = generate_key_pair(2048)
        (key1_dir / "private.pem").write_bytes(private1)
        (key1_dir / "public.pem").write_bytes(public1)
        
        # Create key-2024-02
        key2_dir = temp_keys_dir / "key-2024-02"
        key2_dir.mkdir()
        private2, public2 = generate_key_pair(2048)
        (key2_dir / "private.pem").write_bytes(private2)
        (key2_dir / "public.pem").write_bytes(public2)
        
        # Set current to key-2024-02
        (temp_keys_dir / "current").symlink_to("key-2024-02")
        
        return temp_keys_dir
    
    def test_load_keys(self, populated_keys_dir):
        """Test loading keys from directory."""
        manager = KeyRotationManager(keys_dir=populated_keys_dir)
        manager.load_keys()
        
        assert len(manager.keys) == 2
        assert "key-2024-01" in manager.keys
        assert "key-2024-02" in manager.keys
        assert manager.current_key_id == "key-2024-02"
    
    def test_encrypt_with_current_key(self, populated_keys_dir):
        """Test encryption uses current key."""
        manager = KeyRotationManager(keys_dir=populated_keys_dir)
        manager.load_keys()
        
        data = {"test": "data"}
        envelope = manager.encrypt(data, table="test", operation="INSERT")
        
        assert envelope.key_id == "key-2024-02"  # Current key
    
    def test_decrypt_with_correct_key(self, populated_keys_dir):
        """Test decryption uses the key specified in envelope."""
        manager = KeyRotationManager(keys_dir=populated_keys_dir)
        manager.load_keys()
        
        data = {"test": "value", "number": 42}
        
        # Encrypt with current key (key-2024-02)
        envelope = manager.encrypt(data, table="test", operation="INSERT")
        
        # Decrypt - should automatically use key-2024-02
        decrypted = manager.decrypt(envelope)
        
        assert decrypted == data
    
    def test_decrypt_historical_data(self, populated_keys_dir):
        """Test decryption of data encrypted with an old key."""
        manager = KeyRotationManager(keys_dir=populated_keys_dir)
        manager.load_keys()
        
        # Manually encrypt with old key
        old_encryptor = manager._encryptors["key-2024-01"]
        data = {"historical": "data"}
        envelope = old_encryptor.encrypt(data, table="old", operation="INSERT")
        
        # Decrypt should still work (finds key by key_id)
        decrypted = manager.decrypt(envelope)
        
        assert decrypted == data
    
    def test_rotate_key(self, temp_keys_dir):
        """Test key rotation creates new key and sets it as current."""
        manager = KeyRotationManager(keys_dir=temp_keys_dir)
        
        # Create initial key
        new_id = manager.rotate_key("key-initial")
        assert new_id == "key-initial"
        assert manager.current_key_id == "key-initial"
        
        # Rotate to new key
        new_id = manager.rotate_key("key-rotated")
        assert new_id == "key-rotated"
        assert manager.current_key_id == "key-rotated"
        
        # Both keys should be available
        assert len(manager.keys) == 2
    
    def test_list_keys(self, populated_keys_dir):
        """Test listing all keys."""
        manager = KeyRotationManager(keys_dir=populated_keys_dir)
        manager.load_keys()
        
        keys = manager.list_keys()
        
        assert len(keys) == 2
        assert all("key_id" in k for k in keys)
        assert all("is_active" in k for k in keys)
        assert sum(k["is_active"] for k in keys) == 1  # Only one active
    
    def test_encrypt_decrypt_after_rotation(self, temp_keys_dir):
        """Test that old data can be decrypted after key rotation."""
        manager = KeyRotationManager(keys_dir=temp_keys_dir)
        
        # Create first key and encrypt
        manager.rotate_key("key-v1")
        data1 = {"version": 1}
        envelope1 = manager.encrypt(data1, table="t", operation="INSERT")
        
        # Rotate to new key
        manager.rotate_key("key-v2")
        data2 = {"version": 2}
        envelope2 = manager.encrypt(data2, table="t", operation="INSERT")
        
        # Both should be decryptable
        assert manager.decrypt(envelope1) == data1
        assert manager.decrypt(envelope2) == data2
        
        # Envelope 1 used old key, envelope 2 used new key
        assert envelope1.key_id == "key-v1"
        assert envelope2.key_id == "key-v2"
