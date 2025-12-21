"""CRUD operations for Match Results."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .models import MatchResultModel
from ..schemas.match_result import MatchResult, MatchScore, GapAnalysis, MatchCategory


def create_match_result(db: Session, match_result: MatchResult) -> MatchResultModel:
    """Create a new match result in database."""
    db_match = MatchResultModel(
        cv_id=match_result.cv_id,
        job_id=match_result.job_id,
        overall_score=match_result.score.overall_score,
        category=match_result.score.category.value,
        skill_score=match_result.score.skill_score,
        experience_score=match_result.score.experience_score,
        text_similarity=match_result.score.text_similarity,
        matched_skills=match_result.gap_analysis.matched_skills,
        missing_skills=match_result.gap_analysis.missing_skills,
        extra_skills=match_result.gap_analysis.extra_skills,
        skill_match_ratio=match_result.gap_analysis.skill_match_ratio,
        recommendations=match_result.gap_analysis.recommendations,
        rank=match_result.rank,
        matched_at=match_result.matched_at,
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def get_match_results_by_cv(db: Session, cv_id: str) -> List[MatchResultModel]:
    """Get all match results for a specific CV."""
    return db.query(MatchResultModel).filter(MatchResultModel.cv_id == cv_id).all()


def get_match_results_by_job(db: Session, job_id: str) -> List[MatchResultModel]:
    """Get all match results for a specific job."""
    return db.query(MatchResultModel).filter(MatchResultModel.job_id == job_id).all()


def get_match_result(db: Session, cv_id: str, job_id: str) -> Optional[MatchResultModel]:
    """Get match result for specific CV and job combination."""
    return db.query(MatchResultModel).filter(
        MatchResultModel.cv_id == cv_id,
        MatchResultModel.job_id == job_id
    ).first()


def get_top_matches_for_cv(db: Session, cv_id: str, limit: int = 10) -> List[MatchResultModel]:
    """Get top N matches for a CV, ordered by score."""
    return db.query(MatchResultModel).filter(
        MatchResultModel.cv_id == cv_id
    ).order_by(
        MatchResultModel.overall_score.desc()
    ).limit(limit).all()


def get_potential_matches(db: Session, cv_id: str) -> List[MatchResultModel]:
    """Get all potential matches (>75%) for a CV."""
    return db.query(MatchResultModel).filter(
        MatchResultModel.cv_id == cv_id,
        MatchResultModel.category == "potential"
    ).order_by(
        MatchResultModel.overall_score.desc()
    ).all()


def delete_match_result(db: Session, cv_id: str, job_id: str) -> bool:
    """Delete a specific match result."""
    db_match = get_match_result(db, cv_id, job_id)
    if not db_match:
        return False
    
    db.delete(db_match)
    db.commit()
    return True


def delete_matches_by_cv(db: Session, cv_id: str) -> int:
    """Delete all match results for a CV. Returns count of deleted records."""
    count = db.query(MatchResultModel).filter(MatchResultModel.cv_id == cv_id).delete()
    db.commit()
    return count


def match_model_to_schema(db_match: MatchResultModel, job_title: str, company_name: str) -> MatchResult:
    """Convert database model to Pydantic schema."""
    return MatchResult(
        cv_id=db_match.cv_id,
        job_id=db_match.job_id,
        job_title=job_title,
        company_name=company_name,
        score=MatchScore(
            overall_score=db_match.overall_score,
            category=MatchCategory(db_match.category),
            skill_score=db_match.skill_score,
            experience_score=db_match.experience_score,
            text_similarity=db_match.text_similarity,
        ),
        gap_analysis=GapAnalysis(
            matched_skills=db_match.matched_skills or [],
            missing_skills=db_match.missing_skills or [],
            extra_skills=db_match.extra_skills or [],
            skill_match_ratio=db_match.skill_match_ratio,
            recommendations=db_match.recommendations or [],
        ),
        matched_at=db_match.matched_at,
        rank=db_match.rank,
    )
