# Crypto-Replicator

**NIS2Shield Encrypted Twin** - Secure database replication for disaster recovery.

## Overview

The Crypto-Replicator listens to PostgreSQL changes and replicates them to a cloud backup using **hybrid encryption** (AES-256-GCM + RSA-OAEP envelope). The cloud storage **cannot read** the data - only the holder of the private key can decrypt during disaster recovery.

## Architecture

```
┌────────────────┐     NOTIFY      ┌───────────────────┐
│   PostgreSQL   │ ──────────────► │  Crypto-Replicator │
│    (Active)    │                 │     (Python)       │
└────────────────┘                 └─────────┬──────────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    │ 1. Generate AES session key                 │
                    │ 2. Encrypt data with AES-256-GCM            │
                    │ 3. Wrap key with RSA public key             │
                    └────────────────────────┼────────────────────┘
                                             │
                                             ▼ HTTPS
                                  ┌──────────────────────┐
                                  │  Cloud Storage API   │
                                  │  (Cannot decrypt!)   │
                                  └──────────────────────┘
```

## Quick Start

### 1. Generate RSA Key Pair

```bash
# Generate key pair (keep private key OFFLINE!)
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out cloud.pub

# Put public key where Docker can find it
mkdir -p keys
cp cloud.pub keys/
```

### 2. Configure

```bash
# Required
export DATABASE_URL=postgresql://user:pass@db:5432/mydb
export CLOUD_API_URL=https://your-cloud-backup.com/api

# Optional
export RSA_PUBLIC_KEY_PATH=/keys/cloud.pub
export LISTEN_CHANNEL=nis2_changes
export DEBUG=true
```

### 3. Run with Docker

```bash
docker build -t crypto-replicator .
docker run -v ./keys:/keys:ro crypto-replicator
```

### 4. Set Up Database Triggers

```sql
-- Create notification function
CREATE OR REPLACE FUNCTION notify_audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('nis2_changes', 
        json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'data', row_to_json(NEW)
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to your tables
CREATE TRIGGER trg_audit_notify
AFTER INSERT OR UPDATE OR DELETE ON nis2_audit_log
FOR EACH ROW EXECUTE FUNCTION notify_audit_changes();
```

## Disaster Recovery

When you need to restore:

1. Download encrypted envelopes from cloud
2. Use your private key (from secure offline storage)
3. Run the decryption script

```python
from crypto_replicator.crypto import HybridDecryptor, EncryptedEnvelope

decryptor = HybridDecryptor(private_key_path="private.pem")

for envelope_json in downloaded_envelopes:
    envelope = EncryptedEnvelope.from_json(envelope_json)
    data = decryptor.decrypt(envelope)
    # Restore data to new database
```

## Security Features

- **AES-256-GCM**: Authenticated encryption (confidentiality + integrity)
- **RSA-OAEP**: Asymmetric key wrapping (2048+ bits)
- **Forward Secrecy**: Unique session key per message
- **Non-root**: Docker runs as unprivileged user
- **Zero-trust Cloud**: Cloud cannot decrypt data

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## License

MIT - Part of the [NIS2Shield](https://nis2shield.com) ecosystem.
