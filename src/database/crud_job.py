"""CRUD operations for Jobs."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .models import JobModel
from ..schemas.job import JobPosting, JobRequirements, JobLevel, JobType


def create_job(db: Session, job: JobPosting) -> JobModel:
    """Create a new job in database."""
    db_job = JobModel(
        job_id=job.job_id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        is_remote=job.is_remote,
        job_type=job.job_type.value,
        level=job.level.value if job.level else None,
        description=job.description,
        requirements_text=job.requirements_text,
        required_skills=job.requirements.required_skills,
        preferred_skills=job.requirements.preferred_skills,
        experience_years_min=job.requirements.experience_years_min,
        experience_years_max=job.requirements.experience_years_max,
        education_level=job.requirements.education_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_text=job.salary_text,
        benefits=job.benefits,
        source=job.source,
        source_url=job.source_url,
        posted_date=job.posted_date,
        crawled_at=job.crawled_at,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job(db: Session, job_id: str) -> Optional[JobModel]:
    """Get job by ID."""
    return db.query(JobModel).filter(JobModel.job_id == job_id).first()


def get_all_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[JobModel]:
    """Get all jobs with pagination."""
    return db.query(JobModel).offset(skip).limit(limit).all()


def get_jobs_by_company(db: Session, company_name: str) -> List[JobModel]:
    """Get all jobs from a specific company."""
    return db.query(JobModel).filter(JobModel.company_name.ilike(f"%{company_name}%")).all()


def get_jobs_by_source(db: Session, source: str) -> List[JobModel]:
    """Get all jobs from a specific source (e.g., 'itviec', 'topdev')."""
    return db.query(JobModel).filter(JobModel.source == source).all()


def update_job(db: Session, job_id: str, job: JobPosting) -> Optional[JobModel]:
    """Update existing job."""
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    db_job.title = job.title
    db_job.company_name = job.company_name
    db_job.location = job.location
    db_job.is_remote = job.is_remote
    db_job.job_type = job.job_type.value
    db_job.level = job.level.value if job.level else None
    db_job.description = job.description
    db_job.requirements_text = job.requirements_text
    db_job.required_skills = job.requirements.required_skills
    db_job.preferred_skills = job.requirements.preferred_skills
    db_job.experience_years_min = job.requirements.experience_years_min
    db_job.experience_years_max = job.requirements.experience_years_max
    db_job.education_level = job.requirements.education_level
    db_job.salary_min = job.salary_min
    db_job.salary_max = job.salary_max
    db_job.benefits = job.benefits
    db_job.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: str) -> bool:
    """Delete job by ID."""
    db_job = get_job(db, job_id)
    if not db_job:
        return False
    
    db.delete(db_job)
    db.commit()
    return True


def job_model_to_schema(db_job: JobModel) -> JobPosting:
    """Convert database model to Pydantic schema."""
    return JobPosting(
        job_id=db_job.job_id,
        title=db_job.title,
        company_name=db_job.company_name,
        location=db_job.location,
        is_remote=db_job.is_remote,
        job_type=JobType(db_job.job_type),
        level=JobLevel(db_job.level) if db_job.level else None,
        description=db_job.description,
        requirements_text=db_job.requirements_text,
        requirements=JobRequirements(
            required_skills=db_job.required_skills or [],
            preferred_skills=db_job.preferred_skills or [],
            experience_years_min=db_job.experience_years_min,
            experience_years_max=db_job.experience_years_max,
            education_level=db_job.education_level,
        ),
        salary_min=db_job.salary_min,
        salary_max=db_job.salary_max,
        salary_currency=db_job.salary_currency,
        salary_text=db_job.salary_text,
        benefits=db_job.benefits or [],
        source=db_job.source,
        source_url=db_job.source_url,
        posted_date=db_job.posted_date,
        crawled_at=db_job.crawled_at,
    )
