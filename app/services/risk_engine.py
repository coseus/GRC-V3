from __future__ import annotations


MATURITY_LABELS = {
    0: "Not Implemented",
    1: "Initial",
    2: "Repeatable",
    3: "Defined",
    4: "Managed",
    5: "Optimized",
}

RISK_MULTIPLIER = {
    "Low": 0.8,
    "Medium": 1.0,
    "High": 1.3,
    "Critical": 1.6,
}


def normalize_responses(responses):
    if responses is None:
        return []

    if isinstance(responses, dict):
        return [r for r in responses.values() if isinstance(r, dict)]

    if isinstance(responses, list):
        return [r for r in responses if isinstance(r, dict)]

    return []


def get_domain_name(row: dict) -> str:
    return (
        row.get("domain_name")
        or row.get("domain")
        or row.get("domain_code")
        or row.get("domain_id")
        or "General"
    )


def get_question_name(row: dict) -> str:
    return (
        row.get("question_text")
        or row.get("question")
        or row.get("question_id")
        or row.get("question_code")
        or "Unknown Question"
    )


def get_weight(row: dict) -> float:
    value = row.get("weight", 1)
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 1.0


def get_score(row: dict):
    value = row.get("score")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_risk_label(row: dict) -> str:
    raw = str(row.get("risk", "Medium") or "Medium").strip().title()
    return raw if raw in RISK_MULTIPLIER else "Medium"


def score_to_maturity(score: float | None) -> int:
    if score is None:
        return 0
    if score >= 95:
        return 5
    if score >= 80:
        return 4
    if score >= 60:
        return 3
    if score >= 40:
        return 2
    if score > 0:
        return 1
    return 0


def maturity_label(level: int) -> str:
    return MATURITY_LABELS.get(level, "Unknown")


def calculate_weighted_domain_scores(responses):
    rows = normalize_responses(responses)

    totals = {}
    weights = {}

    for row in rows:
        score = get_score(row)
        if score is None:
            continue

        domain = get_domain_name(row)
        weight = get_weight(row)

        totals[domain] = totals.get(domain, 0.0) + (score * weight)
        weights[domain] = weights.get(domain, 0.0) + weight

    result = {}
    for domain, total in totals.items():
        w = weights.get(domain, 0.0)
        result[domain] = round(total / w, 2) if w else 0.0

    return result


def calculate_domain_maturity(responses):
    domain_scores = calculate_weighted_domain_scores(responses)
    return {
        domain: {
            "score": score,
            "maturity_level": score_to_maturity(score),
            "maturity_label": maturity_label(score_to_maturity(score)),
        }
        for domain, score in domain_scores.items()
    }


def calculate_overall_weighted_score(responses):
    rows = normalize_responses(responses)

    total = 0.0
    total_weight = 0.0

    for row in rows:
        score = get_score(row)
        if score is None:
            continue

        weight = get_weight(row)
        total += score * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(total / total_weight, 2)


def apply_risk_penalty(responses, overall_score: float):
    rows = normalize_responses(responses)
    adjusted = float(overall_score)

    critical_fails = sum(
        1 for row in rows
        if get_risk_label(row) == "Critical" and (get_score(row) or 0.0) < 50
    )
    high_fails = sum(
        1 for row in rows
        if get_risk_label(row) == "High" and (get_score(row) or 0.0) < 50
    )

    if critical_fails >= 1:
        adjusted *= 0.85
    if critical_fails >= 3:
        adjusted *= 0.85
    if high_fails >= 5:
        adjusted *= 0.90

    return round(max(adjusted, 0.0), 2)


def get_maturity_level(score: float) -> str:
    level = score_to_maturity(score)
    return maturity_label(level)


def calculate_risk_score(responses):
    rows = normalize_responses(responses)

    if not rows:
        return 0.0

    total_risk = 0.0
    count = 0

    for row in rows:
        score = get_score(row)
        if score is None:
            continue

        base = 100.0 - score
        risk = get_risk_label(row)
        multiplier = RISK_MULTIPLIER.get(risk, 1.0)

        total_risk += base * multiplier
        count += 1

    if count == 0:
        return 0.0

    return round(total_risk / count, 2)


def get_top_gaps(responses, limit: int = 10):
    rows = normalize_responses(responses)

    ranked = []
    for row in rows:
        score = get_score(row)
        if score is None:
            continue

        ranked.append(
            {
                "domain": get_domain_name(row),
                "question": get_question_name(row),
                "score": score,
                "weight": get_weight(row),
                "risk": get_risk_label(row),
                "maturity_level": score_to_maturity(score),
                "maturity_label": maturity_label(score_to_maturity(score)),
                "notes": row.get("notes") or row.get("comment") or "",
            }
        )

    ranked.sort(
        key=lambda x: (
            x["maturity_level"],
            x["score"],
            0 if x["risk"] == "Critical" else 1 if x["risk"] == "High" else 2,
            -x["weight"],
        )
    )
    return ranked[:limit]


def calculate_vendor_risk_profile(
    responses,
    vendor_criticality: str = "high",
    internet_exposed: bool = True,
    privileged_access: bool = False,
    personal_data_access: bool = True,
):
    overall = calculate_overall_weighted_score(responses)
    adjusted = apply_risk_penalty(responses, overall)
    risk_score = calculate_risk_score(responses)

    vendor_multiplier = 1.0
    criticality = (vendor_criticality or "high").strip().lower()

    if criticality == "critical":
        vendor_multiplier += 0.25
    elif criticality == "high":
        vendor_multiplier += 0.15
    elif criticality == "medium":
        vendor_multiplier += 0.05

    if internet_exposed:
        vendor_multiplier += 0.10
    if privileged_access:
        vendor_multiplier += 0.20
    if personal_data_access:
        vendor_multiplier += 0.10

    inherent_risk = min(round(risk_score * vendor_multiplier, 2), 100.0)

    if inherent_risk >= 75:
        tier = "Tier 1 - Critical"
    elif inherent_risk >= 55:
        tier = "Tier 2 - High"
    elif inherent_risk >= 35:
        tier = "Tier 3 - Medium"
    else:
        tier = "Tier 4 - Low"

    return {
        "overall_score": overall,
        "adjusted_score": adjusted,
        "maturity": get_maturity_level(adjusted),
        "risk_score": risk_score,
        "inherent_vendor_risk": inherent_risk,
        "vendor_tier": tier,
        "top_gaps": get_top_gaps(responses, limit=8),
    }
