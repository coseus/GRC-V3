from __future__ import annotations

from app.services.crosswalk_service import CrosswalkService
from app.services.risk_engine import (
    get_domain_name,
    get_question_name,
    get_risk_label,
    get_score,
    get_weight,
    normalize_responses,
)


class RoadmapService:
    def __init__(self):
        self.crosswalk = CrosswalkService()

    def build_roadmap(self, responses):
        rows = normalize_responses(responses)

        quick_wins = []
        strategic = []

        for row in rows:
            score = get_score(row)
            if score is None:
                continue

            risk = get_risk_label(row)
            weight = get_weight(row)
            domain = get_domain_name(row)
            question = get_question_name(row)

            family = self.crosswalk.suggest_family_from_question(question, domain)
            mapping = self.crosswalk.get_for_family(family)

            item = {
                "Domain": domain,
                "Question": question,
                "Current Score": score,
                "Risk": risk,
                "Weight": weight,
                "Control Family": mapping["label"] if mapping else family,
                "Crosswalk ISO": ", ".join(mapping.get("iso27001", [])) if mapping else "",
                "Crosswalk NIST": ", ".join(mapping.get("nist_csf", [])) if mapping else "",
                "Crosswalk NIS2": ", ".join(mapping.get("nis2", [])) if mapping else "",
            }

            if score < 50 and risk in {"Critical", "High"}:
                item["Priority"] = "Strategic"
                item["Action Horizon"] = "30-90 days"
                strategic.append(item)
            elif score < 70:
                item["Priority"] = "Quick Win"
                item["Action Horizon"] = "0-30 days"
                quick_wins.append(item)

        quick_wins.sort(key=lambda x: (x["Current Score"], x["Risk"] != "High"))
        strategic.sort(key=lambda x: (x["Current Score"], x["Risk"] != "Critical"))

        return {
            "quick_wins": quick_wins,
            "strategic": strategic,
        }
