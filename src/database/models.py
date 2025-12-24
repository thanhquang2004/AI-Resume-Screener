"""SQLAlchemy database models."""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base


class CVModel(Base):
    """CV/Resume database model."""
    
    __tablename__ = "cvs"
    
    # Primary key
    cv_id = Column(String(50), primary_key=True, index=True)
    
    # Basic info
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    
    # Candidate info
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Skills (stored as JSON array)
    technical_skills = Column(JSON, default=[])
    soft_skills = Column(JSON, default=[])
    all_skills = Column(JSON, default=[])
    
    # Experience
    total_experience_years = Column(Float, default=0.0)
    experiences = Column(JSON, default=[])  # Array of experience objects
    
    # Education
    education = Column(JSON, default=[])  # Array of education objects
    highest_education = Column(String(50), default="bachelor")
    
    # Raw text
    raw_text = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    match_results = relationship("MatchResultModel", back_populates="cv", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CVModel(cv_id={self.cv_id}, name={self.name})>"


class JobModel(Base):
    """Job posting database model."""
    
    __tablename__ = "jobs"
    
    # Primary key
    job_id = Column(String(255), primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=False)
    
    # Job details
    job_type = Column(String(50), default="full-time")
    level = Column(String(50), nullable=True)
    
    # Content
    description = Column(Text, default="")
    requirements_text = Column(Text, default="")
    
    # Requirements (stored as JSON)
    required_skills = Column(JSON, default=[])
    preferred_skills = Column(JSON, default=[])
    experience_years_min = Column(Integer, nullable=True)
    experience_years_max = Column(Integer, nullable=True)
    education_level = Column(String(50), nullable=True)
    
    # Salary
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="VND")
    salary_text = Column(String(255), nullable=True)
    
    # Benefits
    benefits = Column(JSON, default=[])
    
    # Metadata
    source = Column(String(50), default="manual", index=True)
    source_url = Column(String(512), nullable=True)
    posted_date = Column(DateTime, nullable=True)
    crawled_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    match_results = relationship("MatchResultModel", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobModel(job_id={self.job_id}, title={self.title}, company={self.company_name})>"


class MatchResultModel(Base):
    """Match result database model."""
    
    __tablename__ = "match_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    cv_id = Column(String(50), ForeignKey("cvs.cv_id"), nullable=False, index=True)
    job_id = Column(String(255), ForeignKey("jobs.job_id"), nullable=False, index=True)
    
    # Match scores
    overall_score = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # potential, review_needed, not_suitable
    skill_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    text_similarity = Column(Float, default=0.0)
    
    # Gap analysis (stored as JSON)
    matched_skills = Column(JSON, default=[])
    missing_skills = Column(JSON, default=[])
    extra_skills = Column(JSON, default=[])
    skill_match_ratio = Column(Float, default=0.0)
    recommendations = Column(JSON, default=[])
    
    # Metadata
    rank = Column(Integer, nullable=True)
    matched_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    cv = relationship("CVModel", back_populates="match_results")
    job = relationship("JobModel", back_populates="match_results")
    
    def __repr__(self):
        return f"<MatchResultModel(cv_id={self.cv_id}, job_id={self.job_id}, score={self.overall_score})>"
