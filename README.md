# GRC Refactor pe fisiere

Aplicatie Streamlit modulara pentru evaluari GRC.

## Ce include
- SQLAlchemy models
- initializare DB fara Alembic
- Alembic optional
- RBAC in service layer
- audit logging
- validare framework-uri
- export PDF / Word
- administrare utilizatori din UI

## Structura
- `app/db/` conexiune, modele, init DB
- `app/repositories/` acces DB
- `app/services/` business logic + RBAC
- `app/schemas/` validare framework
- `app/frameworks/` loader + registry
- `app/exports/` exporturi
- `app/charts/` dashboard charts
- `app/ui/` componente Streamlit
- `app/audit/` audit service
- `alembic/` migrations optionale
- `scripts/` utilitare

## Rulare rapida, fara Alembic
```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app/main.py