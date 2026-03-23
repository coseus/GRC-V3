from __future__ import annotations

from app.services.risk_engine import (
    calculate_overall_weighted_score,
    calculate_risk_score,
    calculate_weighted_domain_scores,
    get_maturity_level as _get_maturity_level,
)


def calculate_scores(responses):
    return calculate_weighted_domain_scores(responses)


def calculate_overall_score(domain_scores):
    if isinstance(domain_scores, dict):
        if not domain_scores:
            return 0.0
        return round(sum(domain_scores.values()) / len(domain_scores), 2)

    return calculate_overall_weighted_score(domain_scores)


def get_maturity_level(score: float):
    return _get_maturity_level(score)


def get_risk_score(responses):
    return calculate_risk_score(responses)