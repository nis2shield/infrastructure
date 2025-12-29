# NIS2 Shield - Compliance Engine (PRO)

**⚠️ PROPRIETARY & CONFIDENTIAL ⚠️**

This repository contains the commercial "Compliance as Code" engine for NIS2 Shield.
It is NOT Open Source. It is part of the **Pro Compliance** subscription (€12k/year).

## 🚀 Components

1.  **Audit Orchestrator (`main.py`)**:
    *   Parses `tfsec`, `gitleaks`, and CI logs.
    *   Generates the "Living Document" `NIS2_SELF_ASSESSMENT.md`.
    *   Cryptographically signs the report (Planned).

2.  **Probes (`probes/`)**:
    *   `log_analyzer.py`: Advanced forensic analysis of operational logs (Backups, Disaster Recovery).
    *   Supply Chain Validator (Planned).
    *   SIEM Integration Connectors (Splunk, QRadar).

## 📦 Deployment

This engine is distributed as a sealed Docker container or Python package to authorized clients only.

```bash
# Run the auditor (requires license key)
python3 main.py --report-file ../docs/NIS2_SELF_ASSESSMENT.md --sign w/private-key.pem
```

## 🛡️ License

Copyright (C) 2025 Fabrizio Di Priamo / NIS2 Shield Team.
All Rights Reserved. Unauthorized copying of this file, via any medium is strictly prohibited.
