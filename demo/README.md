# NIS2 Shield Full-Stack Demo

This demo showcases the complete NIS2 Shield ecosystem:
- **Backend**: Django with `django-nis2-shield` middleware
- **Frontend**: React with `@nis2shield/react-guard`  
- **Infrastructure**: Hardened containers with log segregation

## Quick Start

### Option 1: Local Docker

```bash
# Clone and start
git clone https://github.com/nis2shield/infrastructure.git
cd infrastructure/demo

# Set environment variables (or use defaults for demo)
export DB_PASSWORD=demo_secret
export SECRET_KEY=your-secret-key

# Start all services
docker compose up -d

# Access:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs/
```

### Option 2: One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/nis2shield)

## Demo Features

| Feature | Description |
|---------|-------------|
| **Login Flow** | See forensic logging in action |
| **Rate Limiting** | Trigger 429 after 10 rapid requests |
| **Session Guard** | Watch for hijacking detection |
| **Idle Timeout** | SessionWatchdog demo (15 min) |
| **Secure Storage** | AES-GCM encrypted localStorage |
| **Telemetry** | React → Django event flow |

## Test Credentials

```
Email: demo@nis2shield.com
Password: Nis2Demo2024!
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  Django Backend │
│  @nis2shield/   │     │  django-nis2-   │
│  react-guard    │     │  shield         │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼─────┐           ┌───────▼───────┐
              │ PostgreSQL│           │  Fluent Bit   │
              │  (Data)   │           │  (→ SIEM)     │
              └───────────┘           └───────────────┘
```

## NIS2 Compliance Demo

Run the compliance check:

```bash
docker compose exec backend python manage.py check_nis2
```

Expected output:
```
[NIS2 SHIELD AUDIT REPORT]
───────────────────────────────────
[PASS] Forensic Logging active (JSON)
[PASS] PII Encryption enabled
[PASS] Session Cookie Secure
[PASS] Rate Limiting enabled
───────────────────────────────────
COMPLIANCE SCORE: 100/100
```

## Cleanup

```bash
docker compose down -v
```
