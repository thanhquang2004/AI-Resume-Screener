"""
Job Posting schema definitions.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobLevel(str, Enum):
    """Job experience levels."""
    INTERN = "intern"
    FRESHER = "fresher"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"


class JobType(str, Enum):
    """Job types."""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    REMOTE = "remote"
    HYBRID = "hybrid"


class JobRequirements(BaseModel):
    """Extracted requirements from JD."""
    
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    education_level: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)


class JobPosting(BaseModel):
    """Schema for Job Posting (JD) data."""
    
    # Identification
    job_id: str = Field(..., description="Unique job identifier")
    
    # Basic info
    title: str = Field(..., description="Job title")
    company_name: str = Field(..., description="Company name")
    
    # Location
    location: Optional[str] = None
    is_remote: bool = False
    
    # Job details
    job_type: JobType = JobType.FULL_TIME
    level: Optional[JobLevel] = None
    
    # Content
    description: str = Field(default="", description="Full job description")
    requirements_text: str = Field(default="", description="Raw requirements text")
    
    # Extracted requirements
    requirements: JobRequirements = Field(default_factory=JobRequirements)
    
    # Salary
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "VND"
    salary_text: Optional[str] = None
    
    # Benefits
    benefits: List[str] = Field(default_factory=list)
    
    # Metadata
    source: str = Field(default="manual", description="Source website")
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    crawled_at: datetime = Field(default_factory=datetime.now)
    
    # Vector (populated after processing)
    text_vector: Optional[List[float]] = None
    
    def get_full_text(self) -> str:
        """Get all text content for vectorization."""
        parts = [
            self.title,
            self.description,
            self.requirements_text,
            " ".join(self.requirements.required_skills),
            " ".join(self.requirements.preferred_skills),
        ]
        return " ".join(filter(None, parts))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobPostingCreate(BaseModel):
    """Schema for creating a job posting."""
    
    title: str
    company_name: str
    description: str
    requirements_text: str = ""
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
