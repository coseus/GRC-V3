# README GRC V3

# 🛡️ GRC Assessment Platform

A modern **Governance, Risk & Compliance (GRC)** assessment platform built with **Python + Streamlit**, designed for:

- Internal audits
- External compliance assessments
- Multi-framework security evaluations (NIS2, ISO 27001, NIST, etc.)
- Executive reporting & risk analysis

---

## 🚀 Features

### 📊 Assessment Engine

- Multi-domain, multi-framework assessments
- 150+ enterprise-grade controls
- Weighted scoring model
- Risk-based evaluation (Low / Medium / High / Critical)
- Evidence & notes per control

---

### 🧠 Intelligent Scoring & Risk Engine

- Weighted domain scoring
- Adjusted score (risk penalty applied)
- Risk score calculation
- Maturity model (Initial → Optimized)
- Automatic gap detection

---

### 📈 Framework Comparison Dashboard

- Compare multiple assessments
- Bar chart visualization
- Heatmap per framework
- Highlights:
    - Best framework
    - Weakest framework
    - Highest risk exposure

---

### 🤖 AI Executive Summary

- Auto-generated executive summary
- Strengths & gaps detection
- Actionable recommendations
- Editable + savable

---

### 📌 Recommendations Engine

- Auto-generated recommendations based on assessment
- Manual recommendations:
    - Domain
    - Risk
    - Responsible
    - Deadline
    - Status
- Priority classification

---

### 📄 Professional Export

Export your assessment in:

- 📕 PDF (with logo, cover page, findings)
- 📘 Word (editable audit report)
- 📊 Excel (full dataset)
- 📦 JSON (backup / transfer)

Includes:

- Executive summary
- Findings by severity
- Annex with all controls
- Roadmap-ready data

---

### 🔄 Import / Backup

- Import Excel assessments
- Import/export JSON
- Full SQLite DB backup & restore

---

## 🏗️ Architecture

```bash
app/
├── ui/                 # Streamlit UI components
├── services/           # Business logic
├── repositories/       # DB access layer
├── db/                 # Models & session
├── frameworks/         # Framework loader + registry
├── exports/            # PDF / Word / Excel generation
├── charts/             # Scoring & visualization
```

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone <repo_url>
cd GRC-V2-main
```

### 2. Create virtual environment

```bash
python3-m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install-r requirements.txt
```

---

## 🔐 Configuration

Create `.env` file in root:

```bash
APP_NAME=GRC Assessment Tool
APP_ENV=development

DATABASE_URL=sqlite:///./assessment.db

SECRET_KEY=change-me

DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123

AUTO_INIT_DB=true

UPLOAD_DIR=uploads
COMPANY_LOGO_PATH=uploads/logo.png
DEFAULT_REPORT_VERSION=1.0
```

---

## ▶️ Run Application

```bash
streamlit run app/main.py
```

Access:

- Local: [http://localhost:8501](http://localhost:8501/)
- Network: http://<your-ip>:8501

---

## 👤 Default Login

```bash
Username: admin
Password: admin123!
```

---

## 📊 Supported Frameworks

- NIS2 (Energy, Gas, Generic)
- ISO 27001
- NIST CSF
- COBIT
- CSA CCM (Cloud Controls Matrix)
- TPRM (Third Party Risk Management)
- Unified Enterprise Framework (cross-mapped)

---

## 🔗 Crosswalk Mapping

Each control can map to multiple frameworks:

- ISO 27001 ↔ NIST CSF
- NIST ↔ NIS2
- CIS Controls
- NIS2 Articles

---

## 📉 Scoring Model

Each control:

- Score: 0 / 50 / 100
- Weight: 1–10
- Risk level: Low → Critical

### Calculations:

- Weighted score
- Adjusted score (risk penalty)
- Risk score
- Maturity level

---

## 📤 Export Details

### PDF / Word includes:

- Cover page (date, auditor, version)
- Executive summary
- Findings by severity:
    - Critical
    - High
    - Medium
    - Low
- Detailed annex

---

## 🧩 Scripts (Optional)

Located in `/scripts`:

- backup / restore DB
- framework normalization (dev only)

---

## 🧹 Cleanup Notes

Removed from runtime:

- Alembic (not used)
- migration scripts
- legacy export modules

---

## 🔮 Roadmap (Next Improvements)

- Role-based access control (RBAC)
- API layer (FastAPI)
- Multi-tenant support
- Dashboard charts (trend over time)
- Evidence file upload & management
- Audit trail logging

---

## ⚠️ Security Notes

- Change default admin credentials
- Set strong `SECRET_KEY`
- Restrict access in production
- Use PostgreSQL instead of SQLite for enterprise

---

## 🧑‍💻 Tech Stack

- Python 3.12+
- Streamlit
- SQLAlchemy
- Pydantic
- Pandas

---

## 📌 Use Cases

- Internal audit teams
- Compliance departments
- Cybersecurity assessments
- NIS2 readiness
- Third-party risk reviews

---

## 📄 License

Internal / Proprietary (adapt as needed)

---

## ✨ Final Note

This platform is designed to behave like a **real enterprise audit tool**, not just a questionnaire:

- Scoring is risk-aware
- Recommendations are actionable
- Reports are audit-ready
