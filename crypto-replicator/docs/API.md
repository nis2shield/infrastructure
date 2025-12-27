# Cloud Receiver API Specification

This document describes the API that cloud backup receivers must implement to work with NIS2Shield Crypto-Replicator.

## Overview

The Crypto-Replicator sends **encrypted envelopes** to a cloud receiver. The receiver stores these envelopes but **cannot decrypt them** - only the holder of the RSA private key can decrypt during disaster recovery.

## Full API Specification

📄 **OpenAPI 3.0**: [openapi.yaml](./openapi.yaml)

You can view this in:
- [Swagger Editor](https://editor.swagger.io/)
- [Stoplight](https://stoplight.io/)
- Any OpenAPI-compatible tool

---

## Quick Reference

### Authentication

All endpoints (except `/health`) require Bearer token authentication:

```http
Authorization: Bearer <your-api-token>
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/envelopes` | Receive single envelope |
| `GET` | `/envelopes` | List envelopes (metadata) |
| `GET` | `/envelopes/{id}` | Get specific envelope |
| `POST` | `/envelopes/bulk` | Batch upload |

---

## Envelope Format

```json
{
  "version": "1.0",
  "timestamp": "2024-12-27T09:00:00Z",
  "table": "nis2_audit_log",
  "operation": "INSERT",
  "encrypted_data": "<base64>",
  "encrypted_key": "<base64>",
  "iv": "<base64>",
  "tag": "<base64>",
  "key_id": "cloud-backup-2024"
}
```

| Field | Description |
|-------|-------------|
| `version` | Envelope format version (currently "1.0") |
| `timestamp` | When the original event occurred |
| `table` | Source database table name |
| `operation` | INSERT, UPDATE, or DELETE |
| `encrypted_data` | AES-256-GCM encrypted JSON data |
| `encrypted_key` | RSA-OAEP wrapped AES session key |
| `iv` | 12-byte initialization vector for GCM |
| `tag` | 16-byte GCM authentication tag |
| `key_id` | Identifier for key rotation |

---

## Implementation Requirements

### Storage

1. Store envelopes **as-is** - do not attempt to parse or modify
2. Assign a unique ID to each envelope
3. Index by `table`, `timestamp`, and `key_id` for efficient querying
4. Support at least 30-day retention

### Security

1. Require TLS 1.2+ for all connections
2. Validate Bearer tokens against your auth system
3. Rate limit to prevent abuse (suggest: 1000 req/min)
4. **Do NOT attempt to decrypt** - you don't have the private key

### Reliability

1. Return `201 Created` only after durable storage
2. Support idempotency via `key_id` + `timestamp` combo
3. Implement retry-friendly error codes (429, 503)

---

## Reference Implementations

### Mock Receiver (for testing)

```bash
cd crypto-replicator/mock_cloud
docker build -t mock-cloud .
docker run -p 8080:8080 mock-cloud
```

### Production Options

- **AWS S3 + Lambda**: Store envelopes as objects
- **Azure Blob + Functions**: Similar approach
- **Self-hosted**: Deploy the Flask mock with PostgreSQL backend

---

## Disaster Recovery

To restore from encrypted backups:

1. Download all envelopes from cloud receiver
2. Obtain RSA private key (from secure offline storage)
3. Run decryption script:

```python
from crypto_replicator.crypto import HybridDecryptor, EncryptedEnvelope

decryptor = HybridDecryptor(private_key_path="private.pem")

for envelope_json in downloaded_envelopes:
    envelope = EncryptedEnvelope.from_json(envelope_json)
    data = decryptor.decrypt(envelope)
    # Restore data to database
```

---

## Support

- GitHub: https://github.com/nis2shield/infrastructure
- Documentation: https://nis2shield.com
