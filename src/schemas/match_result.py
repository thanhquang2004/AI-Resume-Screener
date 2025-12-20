"""
Match result schema definitions.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MatchCategory(str, Enum):
    """Match classification categories."""
    POTENTIAL = "potential"           # > 75%
    REVIEW_NEEDED = "review_needed"   # 50-75%
    NOT_SUITABLE = "not_suitable"     # < 50%


class MatchScore(BaseModel):
    """Detailed matching score breakdown."""
    
    overall_score: float = Field(..., ge=0, le=100, description="Overall match %")
    category: MatchCategory
    
    # Component scores
    skill_score: float = Field(default=0, ge=0, le=100)
    experience_score: float = Field(default=0, ge=0, le=100)
    text_similarity: float = Field(default=0, ge=0, le=1)


class GapAnalysis(BaseModel):
    """Analysis of gaps between CV and JD."""
    
    # Skills gap
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    
    skill_match_ratio: float = Field(default=0, ge=0, le=1)
    
    # Experience gap
    required_experience_years: Optional[float] = None
    candidate_experience_years: float = 0
    experience_gap: float = 0
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    """Complete result of matching a CV against a JD."""
    
    cv_id: str
    job_id: str
    job_title: str
    company_name: str
    
    # Scores
    score: MatchScore
    
    # Gap analysis
    gap_analysis: GapAnalysis
    
    # Metadata
    matched_at: datetime = Field(default_factory=datetime.now)
    rank: Optional[int] = None


class CompanyRanking(BaseModel):
    """
    Ranking of companies/jobs for a single CV.
    Main output: ranked list of potential companies for a candidate.
    """
    
    cv_id: str
    candidate_name: Optional[str] = None
    candidate_skills: List[str] = Field(default_factory=list)
    
    # Ranked list of job matches (sorted by score descending)
    rankings: List[MatchResult] = Field(default_factory=list)
    
    # Summary
    total_jobs_analyzed: int = 0
    potential_count: int = 0
    review_needed_count: int = 0
    not_suitable_count: int = 0
    
    # Top companies
    top_companies: List[str] = Field(default_factory=list)
    
    # Common missing skills
    common_skill_gaps: List[str] = Field(default_factory=list)
    
    generated_at: datetime = Field(default_factory=datetime.now)
    
    def get_potential_jobs(self) -> List[MatchResult]:
        """Get only potential matches (>75%)."""
        return [r for r in self.rankings if r.score.category == MatchCategory.POTENTIAL]
    
    def get_top_n(self, n: int = 5) -> List[MatchResult]:
        """Get top N matches."""
        return self.rankings[:n]
