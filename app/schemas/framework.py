from typing import Literal
from pydantic import BaseModel, Field, field_validator

RiskLevel = Literal["Low", "Medium", "High", "Critical"]
ControlType = Literal["mandatory_nis2", "sector_best_practice", "advanced_maturity"]

class LocalizedText(BaseModel):
    ro: str
    en: str

class QuestionSchema(BaseModel):
    id: str
    text: LocalizedText
    answer_type: str = "score"
    weight: int = Field(default=1, ge=1, le=10)
    risk: RiskLevel
    control_type: ControlType
    recommendation: LocalizedText
    business_impact: str | None = None
    remediation_priority: str | None = None
    effort: str | None = None
    default_owner_role: str | None = None
    applies_to: list[str] = Field(default_factory=list)
    scope: list[str] = Field(default_factory=list)
    control_family: str | None = None
    source_frameworks: list[str] = Field(default_factory=list)
    recommendation_key: str | None = None
    evidence_examples: dict[str, list[str]] = Field(default_factory=dict)
    expected_artifacts: dict[str, list[str]] = Field(default_factory=dict)
    iso27001: list[str] = Field(default_factory=list)
    nist_csf: list[str] = Field(default_factory=list)
    cis_control: list[str] = Field(default_factory=list)
    nis2: list[str] = Field(default_factory=list)
    nis2_article: list[str] = Field(default_factory=list)

class DomainSchema(BaseModel):
    id: str
    name: LocalizedText
    questions: list[QuestionSchema]

class MetaSchema(BaseModel):
    framework: str
    version: str
    scoring: dict[str, int | None] = Field(default_factory=lambda: {"Fail": 0, "Partial": 50, "Pass": 100, "NotApplicable": None})
    default_weight: int = 1

class FrameworkSchema(BaseModel):
    meta: MetaSchema
    domains: list[DomainSchema]

    @field_validator("domains")
    @classmethod
    def validate_non_empty(cls, value):
        if not value:
            raise ValueError("At least one domain is required")
        return value
