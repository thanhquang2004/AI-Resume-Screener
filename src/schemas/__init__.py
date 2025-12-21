"""Schemas package - Pydantic data models."""
from .job import JobPosting, JobPostingCreate, JobRequirements, JobLevel, JobType
from .cv import CVData, Education, Experience, ExtractedCV, EducationLevel
from .match_result import MatchResult, MatchScore, GapAnalysis, CompanyRanking, MatchCategory

__all__ = [
    # Job schemas
    "JobPosting",
    "JobPostingCreate",
    "JobRequirements",
    "JobLevel",
    "JobType",
    # CV schemas
    "CVData",
    "Education",
    "Experience",
    "ExtractedCV",
    "EducationLevel",
    # Match result schemas
    "MatchResult",
    "MatchScore",
    "GapAnalysis",
    "CompanyRanking",
    "MatchCategory",
]
