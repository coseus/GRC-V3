from __future__ import annotations

from app.data.framework_crosswalk import FRAMEWORK_CROSSWALK


class CrosswalkService:
    def list_all(self):
        rows = []
        for key, value in FRAMEWORK_CROSSWALK.items():
            rows.append(
                {
                    "control_family": key,
                    "label": value["label"],
                    "iso27001": ", ".join(value.get("iso27001", [])),
                    "nist_csf": ", ".join(value.get("nist_csf", [])),
                    "nis2": ", ".join(value.get("nis2", [])),
                }
            )
        return rows

    def get_for_family(self, family: str):
        return FRAMEWORK_CROSSWALK.get(family)

    def suggest_family_from_question(self, question_text: str, domain_name: str = ""):
        blob = f"{question_text} {domain_name}".lower()

        rules = [
            ("access_control", ["access", "identity", "mfa", "authentication", "privileged"]),
            ("asset_management", ["asset", "inventory", "cmdb"]),
            ("risk_management", ["risk", "assessment"]),
            ("incident_response", ["incident", "response", "breach", "forensic"]),
            ("business_continuity", ["continuity", "backup", "recovery", "resilience", "dr"]),
            ("supply_chain", ["vendor", "supplier", "third party", "outsourcing", "subcontractor"]),
            ("vulnerability_management", ["patch", "vulnerability", "scan", "remediation"]),
            ("logging_monitoring", ["log", "monitor", "alert", "siem", "detection"]),
            ("crypto_data_protection", ["encrypt", "crypt", "data protection", "key management"]),
            ("governance_policy", ["policy", "governance", "board", "management"]),
        ]

        for family, keywords in rules:
            if any(k in blob for k in keywords):
                return family

        return "governance_policy"
