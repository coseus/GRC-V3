from __future__ import annotations

from sqlalchemy import case

from app.db.models import Recommendation


class RecommendationRepository:
    def __init__(self, session):
        self.session = session

    def list_for_assessment(self, assessment_id: int):
        priority_order = case(
            (Recommendation.priority == "high", 0),
            (Recommendation.priority == "medium", 1),
            (Recommendation.priority == "low", 2),
            else_=3,
        )

        return (
            self.session.query(Recommendation)
            .filter(Recommendation.assessment_id == assessment_id)
            .order_by(priority_order, Recommendation.domain_name.asc(), Recommendation.id.asc())
            .all()
        )

    def get_by_id(self, recommendation_id: int):
        return (
            self.session.query(Recommendation)
            .filter(Recommendation.id == recommendation_id)
            .first()
        )

    def create(self, **kwargs):
        obj = Recommendation(**kwargs)
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete_for_assessment(self, assessment_id: int):
        (
            self.session.query(Recommendation)
            .filter(Recommendation.assessment_id == assessment_id)
            .delete(synchronize_session=False)
        )

    def delete(self, obj):
        self.session.delete(obj)