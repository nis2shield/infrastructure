# NIS2 Shield: Compliance as Code Engine
## Technical Architecture Proposal v2.0

### 1. Executive Summary: "Compliance Dimostrabile"
Il problema fondamentale della compliance è il "Drift": la documentazione dice "Sì", l'infrastruttura dice "No".
**NIS2 Shield Compliance Engine** risolve questo problema trasformando la compliance da **Dichiarativa** (checkbox manuali) a **Dimostrabile** (codice verificato).

Il sistema agisce come un "Auditor Robotico" nella pipeline CI/CD:
1.  **Legge** l'infrastruttura (Terraform, Docker).
2.  **Verifica** i requisiti NIS2 usando tool standard di mercato.
3.  **Blocca** le modifiche non conformi (Break Build).
4.  **Aggiorna** la documentazione (`NIS2_SELF_ASSESSMENT.md`) con link alle prove.

---

### 2. Architettura del Sistema

```mermaid
graph LR
    A[Git Push / PR] --> B[CI Pipeline (GitHub Actions)]
    B --> C{Compliance Engine}
    
    C -->|Probe A: Infra| D[tfsec / checkov]
    C -->|Probe B: Container| E[trivy]
    C -->|Probe C: Secrets| F[gitleaks]
    C -->|Probe D: Ops| G[Log Analyzer]
    
    D & E & F & G --> H[Evaluation Logic]
    
    H -->|Critical Fail| I[❌ Block Merge]
    H -->|Pass / Warn| L[✅ Update Documentation]
```

---

### 3. Dettaglio Implementativo: Le Sonde (Probes)
Invece di scrivere parser custom fragili, "wrappiamo" standard industriali stabili e mappiamo i loro output sui requisiti NIS2.

#### Probe A: Infrastructure Security (NIS2 Art. 21.2.c, f)
*   **Tool**: `tfsec` (output JSON).
*   **Target**: Cartelle `terraform/`.
*   **Mapping Esempio**:
    *   `tfsec rule: AWS003` (S3 encryption) -> **NIS2 Art 21.2.f (Crittografia)**
    *   `tfsec rule: AWS077` (S3 versioning) -> **NIS2 Art 21.2.c (Backup/Disaster Recovery)**
*   **Logic**: Se `AWS003` fallisce, il requisito NIS2 corrispondente è marcato ❌.

#### Probe B: Supply Chain & Vulnerabilities (NIS2 Art. 21.2.d)
*   **Tool**: `trivy` (filesystem & image scanning).
*   **Target**: `Dockerfile`, `requirements.txt`, immagini buildate.
*   **Check**:
    *   CVE critiche non patchate.
    *   Uso di immagini base `latest` (non pinnate).
    *   Dipendenze Python vulnerabili.

#### Probe C: Secrets Detection (Security)
*   **Tool**: `gitleaks` o `trufflehog`.
*   **Target**: Intera codebase (history recente).
*   **Check**: Previene il commit accidentale di chiavi AWS, token, o certificati privati (un classico errore che viola la sicurezza base).

#### Probe D: Operational Continuity (NIS2 Art. 21.2.c)
*   **Tool**: Custom Python Script (`log_analyzer.py`).
*   **Target**: GitHub Actions Run Logs.
*   **Check**:
    *   "Il sistema di backup test (restore-test.sh) è stato eseguito con successo negli ultimi 7 giorni?"
    *   Se sì -> ✅ Pass
    *   Se no (o fail) -> ⚠️ Warning (Drift operativa)

---

### 4. Integrazione CI/CD (Guardrails)

Il workflow GitHub Actions avrà due modalità:

1.  **Blocker (Pull Requests)**:
    *   Esegue Probe A, B, C.
    *   Se trova violazioni CRITICAL (es. hardcoded secrets, S3 bucket pubblico), **il job fallisce**.
    *   Il developer NON può mergiare finché non fixa.

2.  **Reporter (Main/Schedule)**:
    *   Esegue tutte le sonde (inclusa Probe D - Ops).
    *   Genera un report JSON unificato.
    *   Aggiorna dinamicamente `NIS2_SELF_ASSESSMENT.md`.

---

### 5. Report Dinamico (Living Documentation)

Il file `NIS2_SELF_ASSESSMENT.md` diventerà un ibrido Umano/Macchina usando dei magic markers XML-like:

```markdown
| Requisito | Descrizione | Stato | Evidenza Tecnica |
|-----------|-------------|-------|------------------|
| **21.2.c** | Backup & DR | <!--status-21.2.c-->✅ PASS<!--end--> | <!--evidence-21.2.c-->[s3.tf:45](link) (Verified by tfsec)<!--end--> |
| **21.2.f** | Crittografia | <!--status-21.2.f-->❌ FAIL<!--end--> | <!--evidence-21.2.f-->Missing KMS Key (Detected by Compliance Engine)<!--end--> |
```

Il motore cerca questi tag e sostituisce solo il contenuto interno, preservando i commenti manuali dell'auditor altrove.

---

### 6. Roadmap di Sviluppo (MVP 3 Settimane)

#### Settimana 1: Security Guardrails (Probes A & C)
*   Setup di `tfsec` e `gitleaks` in GitHub Actions.
*   Configurazione delle regole (es. ignorare low severity).
*   Blocco delle PR se falliscono.

#### Settimana 2: Supply Chain & Ops (Probes B & D)
*   Integrazione `trivy` per scansione container/dipendenze.
*   Script Python per analizzare i log dei job di backup (Probe D).

#### Settimana 3: The Reporter
*   Script "Injector" che prende i risultati JSON delle sonde.
*   Mappatura JSON: `RuleID` -> `NIS2 Article`.
*   Aggiornamento automatico di `NIS2_SELF_ASSESSMENT.md` e commit.

---

### 7. Valore per il Cliente
1.  **Risparmio Audit**: L'auditor non deve spulciare codice. Clicca sui link nel report.
2.  **Sicurezza Reale**: Impossibile deploysre infrastruttura insicura per distrazione.
3.  **Evergreen**: Il report di compliance è sempre aggiornato all'ultimo commit.