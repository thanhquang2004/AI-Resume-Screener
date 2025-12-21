"""CRUD operations for CVs."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from .models import CVModel
from ..schemas.cv import ExtractedCV, Education, Experience, EducationLevel


def create_cv(db: Session, cv: ExtractedCV) -> CVModel:
    """Create a new CV in database."""
    db_cv = CVModel(
        cv_id=cv.cv_id,
        filename=getattr(cv, 'filename', f"cv_{cv.cv_id}"),
        file_type=getattr(cv, 'file_type', 'unknown'),
        name=cv.name,
        email=cv.email,
        technical_skills=cv.technical_skills,
        soft_skills=cv.soft_skills,
        all_skills=cv.all_skills,
        total_experience_years=cv.total_experience_years,
        experiences=[exp.model_dump() for exp in cv.experiences],
        education=[edu.model_dump() for edu in cv.education],
        highest_education=cv.highest_education.value,
        raw_text=cv.raw_text,
    )
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv


def get_cv(db: Session, cv_id: str) -> Optional[CVModel]:
    """Get CV by ID."""
    return db.query(CVModel).filter(CVModel.cv_id == cv_id).first()


def get_all_cvs(db: Session, skip: int = 0, limit: int = 100) -> List[CVModel]:
    """Get all CVs with pagination."""
    return db.query(CVModel).offset(skip).limit(limit).all()


def update_cv(db: Session, cv_id: str, cv: ExtractedCV) -> Optional[CVModel]:
    """Update existing CV."""
    db_cv = get_cv(db, cv_id)
    if not db_cv:
        return None
    
    db_cv.name = cv.name
    db_cv.email = cv.email
    db_cv.technical_skills = cv.technical_skills
    db_cv.soft_skills = cv.soft_skills
    db_cv.all_skills = cv.all_skills
    db_cv.total_experience_years = cv.total_experience_years
    db_cv.experiences = [exp.model_dump() for exp in cv.experiences]
    db_cv.education = [edu.model_dump() for edu in cv.education]
    db_cv.highest_education = cv.highest_education.value
    db_cv.raw_text = cv.raw_text
    db_cv.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_cv)
    return db_cv


def delete_cv(db: Session, cv_id: str) -> bool:
    """Delete CV by ID."""
    db_cv = get_cv(db, cv_id)
    if not db_cv:
        return False
    
    db.delete(db_cv)
    db.commit()
    return True


def cv_model_to_schema(db_cv: CVModel) -> ExtractedCV:
    """Convert database model to Pydantic schema."""
    return ExtractedCV(
        cv_id=db_cv.cv_id,
        name=db_cv.name,
        email=db_cv.email,
        technical_skills=db_cv.technical_skills or [],
        soft_skills=db_cv.soft_skills or [],
        all_skills=db_cv.all_skills or [],
        total_experience_years=db_cv.total_experience_years,
        experiences=[Experience(**exp) for exp in (db_cv.experiences or [])],
        education=[Education(**edu) for edu in (db_cv.education or [])],
        highest_education=EducationLevel(db_cv.highest_education),
        raw_text=db_cv.raw_text,
    )
