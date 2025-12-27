# Cryptographic Specification

Technical documentation of cryptographic algorithms, parameters, and procedures used in NIS2 Shield Infrastructure.

---

## Overview

NIS2 Shield uses industry-standard cryptography to protect data confidentiality and integrity:

| Layer | Algorithm | Purpose |
|-------|-----------|---------|
| Log encryption | Fernet (AES-128-CBC + HMAC) | PII protection in audit logs |
| Cloud backup data | AES-256-GCM | Authenticated encryption |
| Cloud backup key | RSA-2048-OAEP | Key encapsulation |
| Log signing | HMAC-SHA256 | Integrity verification |

---

## Fernet Encryption (Audit Logs)

Used by `django-nis2-shield` for encrypting PII fields in logs.

### Specification

- **Algorithm**: AES-128-CBC with HMAC-SHA256
- **Library**: `cryptography.fernet`
- **Key derivation**: 32-byte URL-safe base64 encoded
- **IV**: Random 128-bit per encryption
- **Auth tag**: HMAC signature appended

### Key Generation

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()  # 32 bytes, base64 encoded
```

### In Django Settings

```python
NIS2_ENCRYPTION_KEY = os.environ.get('NIS2_ENCRYPTION_KEY')
```

### Security Properties

- ✅ Confidentiality (AES)
- ✅ Integrity (HMAC)
- ✅ Authenticated encryption
- ⚠️ Key must be protected via environment variable or secrets manager

---

## Hybrid Encryption (Crypto-Replicator)

Zero-trust encryption for cloud backup. The cloud provider cannot decrypt data.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Hybrid Encryption                           │
│                                                                 │
│  ┌──────────────┐                         ┌──────────────┐      │
│  │  Plaintext   │                         │ RSA Public   │      │
│  │    (JSON)    │                         │    Key       │      │
│  └──────┬───────┘                         └──────┬───────┘      │
│         │                                        │              │
│         ▼                                        │              │
│  ┌──────────────┐    ┌──────────────┐           │              │
│  │ Generate     │───▶│  AES-256     │           │              │
│  │ Session Key  │    │  Session Key │───────────┘              │
│  │ (32 bytes)   │    │              │                          │
│  └──────────────┘    └──────┬───────┘                          │
│         │                   │                                  │
│         ▼                   ▼                                  │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │  AES-256-GCM │    │  RSA-OAEP    │                          │
│  │  Encryption  │    │  Key Wrap    │                          │
│  └──────┬───────┘    └──────┬───────┘                          │
│         │                   │                                  │
│         ▼                   ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Encrypted Envelope                      │   │
│  │  { encrypted_data, encrypted_key, iv, tag, key_id }     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Algorithm Parameters

| Component | Algorithm | Parameters |
|-----------|-----------|------------|
| Data encryption | AES-256-GCM | 256-bit key, 96-bit IV, 128-bit tag |
| Key encapsulation | RSA-OAEP | 2048-bit, SHA-256, MGF1-SHA256 |
| Session key | CSPRNG | 32 bytes (256 bits) |
| IV generation | CSPRNG | 12 bytes (96 bits) |

### Encrypted Envelope Format

```json
{
  "version": "1.0",
  "timestamp": "2025-12-27T10:00:00.000Z",
  "table": "nis2_audit_log",
  "operation": "INSERT",
  "encrypted_data": "<base64>",
  "encrypted_key": "<base64>",
  "iv": "<base64>",
  "tag": "<base64>",
  "key_id": "key-2025-01"
}
```

### Security Properties

- ✅ Forward secrecy (unique session key per message)
- ✅ Authenticated encryption (GCM mode)
- ✅ Zero-trust cloud (no private key on cloud)
- ✅ Key rotation support (key_id tracking)

---

## RSA Key Pair Management

### Key Generation

```bash
# Generate private key (KEEP OFFLINE!)
openssl genrsa -out private.pem 2048

# Extract public key
openssl rsa -in private.pem -pubout -out public.pem

# Verify key
openssl rsa -in private.pem -check
```

### Key Storage

| Key | Location | Access |
|-----|----------|--------|
| Public key | Container, K8s Secret | Read by Crypto-Replicator |
| Private key | OFFLINE, HSM, Air-gapped | DR only, never in cluster |

### Key Rotation Procedure

1. **Generate new key pair** with date-based ID (e.g., `key-2025-06`)
2. **Deploy new public key** to Crypto-Replicator
3. **Update `KEY_ID`** in configuration
4. **Archive old public key** (for historical reference)
5. **Store new private key offline** alongside old private keys

### KeyRotationManager

```python
from crypto_replicator.key_manager import KeyRotationManager

# Initialize with keys directory
manager = KeyRotationManager(keys_dir="/path/to/keys")
manager.load_keys()

# Rotate to new key
new_key_id = manager.rotate_key("key-2025-06")

# Decrypt with any historical key
data = manager.decrypt(envelope)  # Auto-selects correct key by ID
```

---

## HMAC Log Signing

Audit logs are signed to prevent tampering.

### Algorithm

- **HMAC-SHA256** with 256-bit key
- Signature covers: timestamp, event, user, action

### Verification

```python
import hmac
import hashlib

def verify_log_entry(log_entry, key):
    message = f"{log_entry['timestamp']}{log_entry['event']}{log_entry['user']}"
    expected = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(log_entry['signature'], expected)
```

---

## TLS Configuration

All network communication uses TLS 1.2+.

### Recommended Cipher Suites

```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

### Certificate Requirements

- Minimum 2048-bit RSA or 256-bit ECC
- Valid CA chain
- OCSP stapling recommended

---

## Compliance Mapping

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| NIST SP 800-57 | Key Management | Key rotation, separation |
| NIST SP 800-38D | GCM Mode | AES-256-GCM for data |
| FIPS 140-2 | Approved algorithms | AES, RSA, SHA-256 |
| NIS2 Art. 21(e) | Cryptography | All data encrypted |

---

## Disaster Recovery Decryption

### Prerequisites

- Access to private key(s) for relevant time period
- Encrypted envelopes from cloud storage
- Python environment with `cryptography` library

### Procedure

```bash
# 1. Download encrypted envelopes from cloud
aws s3 sync s3://backup-bucket/envelopes ./envelopes

# 2. Run recovery script
python -m crypto_replicator.recover \
  --keys-dir /secure/keys \
  --input ./envelopes \
  --output ./recovered
```

### Recovery Script Flow

1. Load all private keys from `keys-dir`
2. For each envelope:
   - Match `key_id` to correct private key
   - Decrypt session key with RSA-OAEP
   - Decrypt data with AES-GCM
3. Output plaintext JSON

---

*Last updated: 2025-12-27*
