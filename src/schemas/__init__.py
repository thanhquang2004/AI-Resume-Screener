"""
Schemas package - Pydantic data models.
"""
from .job import JobPosting, JobRequirements
from .cv import CVData, Education, Experience, ExtractedCV
from .match_result import MatchResult, MatchScore, GapAnalysis, CompanyRanking, MatchCategory

__all__ = [
    "JobPosting",
    "JobRequirements",
    "CVData",
    "Education",
    "Experience",
    "ExtractedCV",
    "MatchResult",
    "MatchScore",
    "GapAnalysis",
    "CompanyRanking",
    "MatchCategory",
]
