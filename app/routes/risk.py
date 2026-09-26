from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.risk_analysis import RiskAnalysis
from app.schemas.risk_analysis import (
    RiskAnalysisCreate,
    RiskAnalysisResponse,
    RiskAnalysisUpdate,
)
from app.services.risk_calculator import calculate_risk, classify_score

router = APIRouter(prefix="/risk-analysis", tags=["risk-analysis"])
DbSession = Annotated[Session, Depends(get_db)]


def get_analysis_or_404(analysis_id: int, db: Session) -> RiskAnalysis:
    analysis = db.get(RiskAnalysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Risk analysis not found")
    return analysis


@router.post("", response_model=RiskAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: RiskAnalysisCreate, db: DbSession) -> RiskAnalysis:
    result = calculate_risk(payload)
    analysis = RiskAnalysis(
        trip_id=payload.trip_id,
        score=result.score,
        classification=result.classification.value,
        warnings=result.warnings,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("", response_model=list[RiskAnalysisResponse])
def list_analyses(db: DbSession) -> list[RiskAnalysis]:
    return list(db.scalars(select(RiskAnalysis).order_by(RiskAnalysis.id)).all())


@router.get("/{analysis_id}", response_model=RiskAnalysisResponse)
def get_analysis(analysis_id: int, db: DbSession) -> RiskAnalysis:
    return get_analysis_or_404(analysis_id, db)


@router.put("/{analysis_id}", response_model=RiskAnalysisResponse)
def update_analysis(
    analysis_id: int, payload: RiskAnalysisUpdate, db: DbSession
) -> RiskAnalysis:
    analysis = get_analysis_or_404(analysis_id, db)
    changes = payload.model_dump(exclude_unset=True)
    if "classification" in changes:
        changes["classification"] = changes["classification"].value
    elif "score" in changes:
        changes["classification"] = classify_score(changes["score"]).value
    for field, value in changes.items():
        setattr(analysis, field, value)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int, db: DbSession) -> Response:
    analysis = get_analysis_or_404(analysis_id, db)
    db.delete(analysis)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

