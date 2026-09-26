from dataclasses import dataclass

from app.schemas.risk_analysis import RiskAnalysisCreate, RiskClassification


@dataclass(frozen=True)
class CalculatedRisk:
    score: int
    classification: RiskClassification
    warnings: list[str]


def classify_score(score: int) -> RiskClassification:
    if score <= 30:
        return RiskClassification.LOW
    if score <= 60:
        return RiskClassification.MODERATE
    if score <= 80:
        return RiskClassification.HIGH
    return RiskClassification.CRITICAL


def calculate_risk(data: RiskAnalysisCreate) -> CalculatedRisk:
    score = 0
    warnings: list[str] = []

    if data.precipitation > 10:
        score += 30
        warnings.append("Heavy precipitation")
    if data.wind_speed > 50:
        score += 30
        warnings.append("Strong winds")
    if data.temperature < 5:
        score += 20
        warnings.append("Low temperature")
    elif data.temperature > 40:
        score += 20
        warnings.append("High temperature")

    score = min(score, 100)
    return CalculatedRisk(
        score=score,
        classification=classify_score(score),
        warnings=warnings,
    )

