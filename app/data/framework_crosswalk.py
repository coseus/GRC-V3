from __future__ import annotations

FRAMEWORK_CROSSWALK = {
    "access_control": {
        "label": "Access Control & Identity",
        "iso27001": ["A.5.15", "A.5.16", "A.5.17", "A.8.2", "A.8.3"],
        "nist_csf": ["PR.AA-01", "PR.AA-03", "PR.AA-05"],
        "nis2": ["Art. 21(2)(d)", "Art. 21(2)(i)"],
    },
    "asset_management": {
        "label": "Asset Management",
        "iso27001": ["A.5.9", "A.5.10", "A.5.11"],
        "nist_csf": ["ID.AM-01", "ID.AM-02", "ID.AM-05"],
        "nis2": ["Art. 21(2)(a)"],
    },
    "risk_management": {
        "label": "Risk Management",
        "iso27001": ["6.1.2", "6.1.3", "8.2", "8.3"],
        "nist_csf": ["GV.RM-01", "GV.RM-02", "ID.RA-01"],
        "nis2": ["Art. 21(2)(a)"],
    },
    "incident_response": {
        "label": "Incident Response",
        "iso27001": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28"],
        "nist_csf": ["RS.MA-01", "RS.AN-01", "RS.CO-02", "RS.IM-01"],
        "nis2": ["Art. 21(2)(b)", "Art. 23"],
    },
    "business_continuity": {
        "label": "Business Continuity & Resilience",
        "iso27001": ["A.5.29", "A.5.30"],
        "nist_csf": ["RC.RP-01", "RC.CO-03", "RC.IM-01"],
        "nis2": ["Art. 21(2)(c)"],
    },
    "supply_chain": {
        "label": "Supply Chain / Third Party Risk",
        "iso27001": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
        "nist_csf": ["GV.SC-01", "GV.SC-06", "ID.RA-09"],
        "nis2": ["Art. 21(2)(d)"],
    },
    "vulnerability_management": {
        "label": "Vulnerability & Patch Management",
        "iso27001": ["A.8.8", "A.8.9"],
        "nist_csf": ["ID.RA-01", "PR.PS-03", "DE.CM-08"],
        "nis2": ["Art. 21(2)(f)"],
    },
    "logging_monitoring": {
        "label": "Logging & Monitoring",
        "iso27001": ["A.8.15", "A.8.16"],
        "nist_csf": ["DE.CM-01", "DE.CM-03", "DE.AE-03"],
        "nis2": ["Art. 21(2)(b)", "Art. 21(2)(f)"],
    },
    "crypto_data_protection": {
        "label": "Cryptography & Data Protection",
        "iso27001": ["A.8.24", "A.8.11", "A.8.12"],
        "nist_csf": ["PR.DS-01", "PR.DS-02"],
        "nis2": ["Art. 21(2)(h)"],
    },
    "governance_policy": {
        "label": "Governance & Policy",
        "iso27001": ["5.1", "5.2", "5.3"],
        "nist_csf": ["GV.OC-01", "GV.OC-02", "GV.PO-01"],
        "nis2": ["Art. 20", "Art. 21(1)"],
    },
}
