"""
Integration tests for Crypto-Replicator.

Uses Docker Compose with PostgreSQL and Mock Cloud Receiver.
"""

import json
import os
import time
from unittest.mock import MagicMock

import pytest
import requests

# Skip if not running integration tests
INTEGRATION = os.environ.get("INTEGRATION_TESTS", "false").lower() == "true"
pytestmark = pytest.mark.skipif(not INTEGRATION, reason="Integration tests disabled")


class TestPostgresIntegration:
    """Tests for PostgreSQL listener integration."""
    
    @pytest.fixture
    def db_connection(self):
        """Create a database connection."""
        import psycopg2
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 5432)),
            user=os.environ.get("DB_USER", "nis2user"),
            password=os.environ.get("DB_PASSWORD", "testpass123"),
            dbname=os.environ.get("DB_NAME", "nis2_test"),
        )
        yield conn
        conn.close()
    
    def test_create_table_with_trigger(self, db_connection):
        """Test creating a table with CDC trigger."""
        from crypto_replicator.listener import get_trigger_sql
        
        cursor = db_connection.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_audit (
                id SERIAL PRIMARY KEY,
                action VARCHAR(50),
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create trigger
        trigger_sql = get_trigger_sql("test_audit", "nis2_changes")
        cursor.execute(trigger_sql)
        
        db_connection.commit()
        cursor.close()
        
        # Verify trigger exists
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT trigger_name FROM information_schema.triggers 
            WHERE event_object_table = 'test_audit'
        """)
        triggers = cursor.fetchall()
        cursor.close()
        
        assert len(triggers) > 0
        assert any("trg_test_audit_notify" in t[0] for t in triggers)


class TestMockCloudIntegration:
    """Tests for Mock Cloud Receiver integration."""
    
    @pytest.fixture
    def cloud_url(self):
        return os.environ.get("CLOUD_URL", "http://localhost:8080")
    
    def test_health_endpoint(self, cloud_url):
        """Test mock cloud health endpoint."""
        response = requests.get(f"{cloud_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "envelopes_received" in data
    
    def test_receive_envelope(self, cloud_url):
        """Test sending an envelope to mock cloud."""
        envelope = {
            "version": "1.0",
            "timestamp": "2024-12-27T09:00:00Z",
            "table": "test_table",
            "operation": "INSERT",
            "encrypted_data": "base64encrypteddata==",
            "encrypted_key": "base64encryptedkey==",
            "iv": "base64iv==",
            "tag": "base64tag==",
            "key_id": "test-key"
        }
        
        # Clear previous envelopes
        requests.delete(f"{cloud_url}/envelopes")
        
        # Send envelope
        response = requests.post(
            f"{cloud_url}/envelopes",
            json=envelope,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "accepted"
        assert "id" in data
        
        # Verify envelope was stored
        response = requests.get(f"{cloud_url}/envelopes")
        assert response.status_code == 200
        assert response.json()["count"] == 1


class TestEndToEnd:
    """End-to-end tests of the full encryption pipeline."""
    
    @pytest.fixture
    def keys(self):
        """Generate test keys."""
        from crypto_replicator.crypto import generate_key_pair
        return generate_key_pair(2048)
    
    def test_full_encryption_to_cloud(self, keys):
        """Test encrypting data and sending to mock cloud."""
        from crypto_replicator.crypto import HybridEncryptor, HybridDecryptor, EncryptedEnvelope
        
        private_pem, public_pem = keys
        
        # Encrypt
        encryptor = HybridEncryptor(public_key_pem=public_pem, key_id="e2e-test")
        original_data = {
            "user_id": 42,
            "action": "login",
            "ip": "10.0.0.1"
        }
        
        envelope = encryptor.encrypt(
            data=original_data,
            table="audit_log",
            operation="INSERT"
        )
        
        # Send to mock cloud
        cloud_url = os.environ.get("CLOUD_URL", "http://localhost:8080")
        response = requests.post(
            f"{cloud_url}/envelopes",
            data=envelope.to_json(),
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        
        # Retrieve and decrypt
        envelope_id = response.json()["id"]
        response = requests.get(f"{cloud_url}/envelopes/{envelope_id}")
        stored = response.json()
        
        # Rebuild envelope (without metadata)
        recovered_envelope = EncryptedEnvelope(
            version=stored["version"],
            timestamp=stored["timestamp"],
            table=stored["table"],
            operation=stored["operation"],
            encrypted_data=stored["encrypted_data"],
            encrypted_key=stored["encrypted_key"],
            iv=stored["iv"],
            tag=stored["tag"],
            key_id=stored["key_id"],
        )
        
        # Decrypt
        decryptor = HybridDecryptor(private_key_pem=private_pem)
        decrypted = decryptor.decrypt(recovered_envelope)
        
        assert decrypted == original_data
