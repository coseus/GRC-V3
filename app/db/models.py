from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def utcnow():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="viewer", index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    created_assessments = relationship(
        "Assessment",
        back_populates="creator",
        foreign_keys="Assessment.created_by",
    )
    answers = relationship(
        "Answer",
        back_populates="answered_by_user",
        foreign_keys="Answer.answered_by",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="actor",
        foreign_keys="AuditLog.actor_user_id",
    )
    executive_summaries = relationship(
        "ExecutiveSummary",
        back_populates="author",
        foreign_keys="ExecutiveSummary.updated_by",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="author",
        foreign_keys="Recommendation.updated_by",
    )


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    assessments = relationship(
        "Assessment",
        back_populates="company",
        cascade="all, delete-orphan",
    )


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_assessment_company_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    framework_code = Column(String(100), nullable=False, index=True)
    framework_name = Column(String(255), nullable=False)
    framework_version = Column(String(50), nullable=False, default="1.0")

    status = Column(String(50), nullable=False, default="draft", index=True)
    is_locked = Column(Boolean, nullable=False, default=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime, nullable=True)

    framework_snapshot_json = Column(Text, nullable=True)

    company = relationship("Company", back_populates="assessments")
    creator = relationship(
        "User",
        back_populates="created_assessments",
        foreign_keys=[created_by],
    )
    answers = relationship(
        "Answer",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    executive_summary = relationship(
        "ExecutiveSummary",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_code", name="uq_answer_assessment_question"),
    )

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_code = Column(String(100), nullable=False, index=True)
    question_text = Column(Text, nullable=True)
    domain_code = Column(String(100), nullable=True, index=True)
    domain_name = Column(String(255), nullable=True)

    selected_value = Column(String(50), nullable=True)
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    weight = Column(Float, nullable=False, default=1.0)

    comment = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="answered")

    answered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    answered_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    assessment = relationship("Assessment", back_populates="answers")
    answered_by_user = relationship(
        "User",
        back_populates="answers",
        foreign_keys=[answered_by],
    )

    @property
    def question_id(self):
        return self.question_code

    @property
    def domain_id(self):
        return self.domain_code

    @property
    def value(self):
        return self.selected_value

    @property
    def answer_value(self):
        return self.selected_value

    @property
    def notes(self):
        return self.comment
    
    @property
    def proof(self):
        return self.evidence


class ExecutiveSummary(Base):
    __tablename__ = "executive_summaries"
    __table_args__ = (
        UniqueConstraint("assessment_id", name="uq_executive_summary_assessment"),
    )

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    summary_text = Column(Text, nullable=True)
    strengths_text = Column(Text, nullable=True)
    gaps_text = Column(Text, nullable=True)
    recommendations_text = Column(Text, nullable=True)

    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    assessment = relationship("Assessment", back_populates="executive_summary")
    author = relationship(
        "User",
        back_populates="executive_summaries",
        foreign_keys=[updated_by],
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    domain_code = Column(String(100), nullable=True, index=True)
    domain_name = Column(String(255), nullable=True, index=True)
    question_code = Column(String(100), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), nullable=False, default="medium", index=True)
    status = Column(String(50), nullable=False, default="open", index=True)

    source = Column(String(50), nullable=False, default="manual", index=True)
    score = Column(Float, nullable=True)

    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    assessment = relationship("Assessment", back_populates="recommendations")
    author = relationship(
        "User",
        back_populates="recommendations",
        foreign_keys=[updated_by],
    )

    @property
    def question_id(self):
        return self.question_code

    @property
    def domain_id(self):
        return self.domain_code


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    details_json = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=utcnow, index=True)

    actor = relationship("User", back_populates="audit_logs")