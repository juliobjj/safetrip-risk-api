from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskClassification(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskAnalysisCreate(BaseModel):
    trip_id: int = Field(gt=0)
    vehicle_type: str = Field(min_length=1, max_length=50)
    temperature: float
    precipitation: float = Field(ge=0)
    wind_speed: float = Field(ge=0)


class RiskAnalysisUpdate(BaseModel):
    score: int | None = Field(default=None, ge=0, le=100)
    classification: RiskClassification | None = None
    warnings: list[str] | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "RiskAnalysisUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class RiskAnalysisResponse(BaseModel):
    id: int
    trip_id: int
    score: int
    classification: RiskClassification
    warnings: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

