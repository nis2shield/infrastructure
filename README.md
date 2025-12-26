# NIS2 Infrastructure Kit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**Secure-by-Design Docker Infrastructure for NIS2 Compliance.**

This repository provides the "last mile" for NIS2 compliance: **secure infrastructure**. While [django-nis2-shield](https://github.com/nis2shield/django-nis2-shield) and [@nis2shield/react-guard](https://github.com/nis2shield/react-guard) protect your code, this kit protects the **execution environment**.

## ✨ Features

- 🔒 **Hardened Containers**: Non-root execution, read-only filesystem
- 📊 **Log Segregation**: Logs exported via sidecar (Fluent Bit)
- 💾 **Automated Backups**: PostgreSQL dumps with retention policy
- 🏗️ **NIS2 Compliant**: Addresses Art. 21 infrastructure requirements

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   webapp     │    │ log-collector│    │  db-backup   │   │
│  │   (Django)   │───▶│ (Fluent Bit) │    │  (Cron)      │   │
│  │              │    │              │    │              │   │
│  │ • Non-root   │    │ • Reads logs │    │ • 6h backup  │   │
│  │ • Read-only  │    │ • SIEM ready │    │ • 7d retain  │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                                       │            │
│         ▼                                       ▼            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2+
- A Docker image of your Django app using `django-nis2-shield`

### Installation

```bash
# Clone the repository
git clone https://github.com/nis2shield/infrastructure.git
cd infrastructure

# Copy environment template
cp .env.example .env

# Edit .env with your values (IMPORTANT: change passwords!)
nano .env

# Start the stack
docker-compose up -d

# Check status
docker-compose ps
```

## ⚙️ Services

### 1. webapp (Application Layer)

Your Django application, hardened with:
- `user: 1000:1000` - Non-root execution
- `read_only: true` - Immutable filesystem
- `tmpfs: /tmp` - RAM-only writable directory

### 2. log-collector (Fluent Bit Sidecar)

Reads logs from shared volume and forwards to:
- **Console** (default, for development)
- **Elasticsearch** (uncomment in config)
- **HTTP/SIEM** (Intrusa, Splunk HEC, etc.)

Edit `monitoring/fluent-bit.conf` to configure outputs.

### 3. db-backup (Business Continuity)

Automated PostgreSQL backups:
- Schedule: `@every 6h00m` (configurable)
- Retention: 7 days (configurable)
- Location: `./backups/`

## 🔄 Disaster Recovery Testing

Test that your backups can be restored (NIS2 Art. 21c requirement):

```bash
# Run the automated restore test
./scripts/restore-test.sh

# Or specify a backup file
./scripts/restore-test.sh ./backups/mybackup.sql.gz
```

The script will:
1. Start an empty PostgreSQL container
2. Restore the latest backup
3. Validate the data integrity
4. Generate a compliance report

Keep the generated report for your NIS2 audit documentation.

## 📁 Project Structure

```
infrastructure/
├── docker-compose.yml      # Service orchestration
├── .env.example            # Environment template
├── monitoring/
│   ├── fluent-bit.conf     # Log collector config
│   └── parsers.conf        # JSON/CEF parsers
├── backups/                # Auto-created, gitignored
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

## 🔐 NIS2 Compliance Matrix

| NIS2 Article | Requirement | Infrastructure Solution |
|--------------|-------------|------------------------|
| Art. 21 (a) | Risk analysis & system security | Hardened containers, non-root |
| Art. 21 (b) | Incident management | Centralized, segregated logs |
| Art. 21 (c) | Business continuity | Automated backups with retention |
| Art. 21 (d) | Supply chain security | Verified base images |
| Art. 21 (e) | Security hygiene | Read-only filesystem |

## 🔧 Configuration

### SIEM Integration

Edit `monitoring/fluent-bit.conf`:

```ini
# Uncomment for Elasticsearch
[OUTPUT]
    Name              es
    Host              ${ELASTICSEARCH_HOST}
    Port              9200
    Index             nis2-logs
```

### Backup Schedule

In `docker-compose.yml` or `.env`:

```yaml
SCHEDULE=@every 6h00m   # Every 6 hours
BACKUP_KEEP_DAYS=7      # Keep 7 days
```

## 🤝 Related Projects

- [django-nis2-shield](https://github.com/nis2shield/django-nis2-shield) - Backend middleware
- [@nis2shield/react-guard](https://github.com/nis2shield/react-guard) - Frontend protection
- [nis2shield.com](https://nis2shield.com) - Documentation hub

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

**Part of the [NIS2 Shield](https://nis2shield.com) ecosystem** 🛡️