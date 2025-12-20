"""
CV/Resume schema definitions.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class EducationLevel(str, Enum):
    """Education levels."""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"


class Education(BaseModel):
    """Education entry in CV."""
    
    institution: Optional[str] = None
    degree: Optional[str] = None
    level: EducationLevel = EducationLevel.BACHELOR
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[float] = None


class Experience(BaseModel):
    """Work experience entry in CV."""
    
    company: Optional[str] = None
    position: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_current: bool = False
    description: Optional[str] = None
    skills_used: List[str] = Field(default_factory=list)


class CVData(BaseModel):
    """Raw CV data after parsing from PDF/DOCX."""
    
    cv_id: str = Field(..., description="Unique CV identifier")
    filename: str
    file_type: str = Field(..., description="pdf/docx")
    raw_text: str = Field(..., description="Raw extracted text")
    parsed_at: datetime = Field(default_factory=datetime.now)


class ExtractedCV(BaseModel):
    """Structured CV data after extraction."""
    
    cv_id: str
    
    # Personal info (can be anonymized)
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    
    # Summary
    summary: Optional[str] = None
    
    # Skills (most important for matching)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    all_skills: List[str] = Field(default_factory=list)
    
    # Experience
    experiences: List[Experience] = Field(default_factory=list)
    total_experience_years: float = 0.0
    
    # Education
    education: List[Education] = Field(default_factory=list)
    highest_education: EducationLevel = EducationLevel.BACHELOR
    
    # Raw text for vectorization
    raw_text: str = ""
    
    # Vector (populated after processing)
    text_vector: Optional[List[float]] = None
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.now)
    
    def get_all_skills(self) -> List[str]:
        """Get all skills combined."""
        skills = set()
        skills.update(s.lower() for s in self.technical_skills)
        skills.update(s.lower() for s in self.soft_skills)
        skills.update(s.lower() for s in self.all_skills)
        return list(skills)
    
    def get_searchable_text(self) -> str:
        """Get all text for vectorization."""
        parts = []
        
        if self.summary:
            parts.append(self.summary)
        
        parts.extend(self.technical_skills)
        parts.extend(self.soft_skills)
        
        for exp in self.experiences:
            if exp.position:
                parts.append(exp.position)
            if exp.description:
                parts.append(exp.description)
            parts.extend(exp.skills_used)
        
        for edu in self.education:
            if edu.field_of_study:
                parts.append(edu.field_of_study)
            if edu.degree:
                parts.append(edu.degree)
        
        if self.raw_text:
            parts.append(self.raw_text)
        
        return " ".join(parts)
