#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: ./scripts/restore.sh <backup_file>"
  exit 1
fi
cp "$1" assessment.db
echo "SQLite restore completed from $1"
