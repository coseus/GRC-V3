from __future__ import annotations

FRAMEWORK_REGISTRY = {
    # =========================
    # MAIN ENTERPRISE AUDIT
    # =========================
    "unified_enterprise": {
        "name": "Unified Enterprise Internal & External Audit",
        "file": "frameworks/unified_enterprise_internal_external_audit.json",
        "description": "Complete enterprise audit covering ISO 27001, NIST CSF, COBIT and governance domains.",
        "category": "enterprise",
    },

    # =========================
    # TPRM / SUPPLY CHAIN
    # =========================
    "tprm_enterprise": {
        "name": "Vendor & Third-Party Risk Management (TPRM)",
        "file": "frameworks/vendor_tprm_supply_chain_assurance.json",
        "description": "End-to-end third-party risk, vendor due diligence and supply chain assurance.",
        "category": "tprm",
    },

    # =========================
    # NIS2 / ENERGY / OT
    # =========================
    "nis2_energy_ot": {
        "name": "NIS2 Energy, OT & Operational Resilience",
        "file": "frameworks/nis2_energy_ot_operational_resilience_audit.json",
        "description": "NIS2 compliance, OT security and operational resilience for energy sector.",
        "category": "regulatory",
    },

    # =========================
    # MEGA (ALL-IN-ONE)
    # =========================
    "mega_enterprise": {
        "name": "Mega Unified Enterprise Assurance",
        "file": "frameworks/mega_unified_enterprise_assurance.json",
        "description": "Full enterprise audit (ALL frameworks combined). Heavy but complete.",
        "category": "full",
    },
}