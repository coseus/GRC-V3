#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
STAMP=$(date +"%Y%m%d_%H%M%S")
if [[ "${DATABASE_URL:-}" == sqlite* ]] || [[ -f assessment.db ]]; then
  cp assessment.db "backups/assessment_${STAMP}.db"
  echo "SQLite backup created: backups/assessment_${STAMP}.db"
else
  echo "For PostgreSQL, run pg_dump based on DATABASE_URL"
fi
