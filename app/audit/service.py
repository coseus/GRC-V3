from __future__ import annotations

import json

from app.db.models import AuditLog


def audit_log(session, actor_user_id, action: str, entity_type: str, entity_id: int | None, details: dict | None):
    row = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details_json=json.dumps(details or {}, ensure_ascii=False),
    )
    session.add(row)