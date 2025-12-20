"""
AI Resume Screener - Main Source Package

A data mining system for matching CVs to Job Descriptions.
For each CV, generates a ranked list of potential companies from high to low.
"""
from .schemas import (
    JobPosting, JobPostingCreate, JobRequirements, JobLevel, JobType,
    CVData, ExtractedCV, Education, Experience, EducationLevel,
    MatchResult, MatchScore, MatchCategory, GapAnalysis, CompanyRanking, RankedJob,
)
from .parsers import CVParser, PDFParser, DocxParser
from .preprocessing import TextCleaner, SkillExtractor, clean_text
from .models import TFIDFVectorizer, CVJobMatcher, MatchClassifier
from .crawlers import JobCrawler, ITViecCrawler, TopDevCrawler
from .utils import SkillDictionary

__version__ = "1.0.0"
__author__ = "AI Resume Screener Team"

__all__ = [
    # Schemas
    "JobPosting", "JobPostingCreate", "JobRequirements", "JobLevel", "JobType",
    "CVData", "ExtractedCV", "Education", "Experience", "EducationLevel",
    "MatchResult", "MatchScore", "MatchCategory", "GapAnalysis", "CompanyRanking", "RankedJob",
    
    # Parsers
    "CVParser", "PDFParser", "DocxParser",
    
    # Preprocessing
    "TextCleaner", "SkillExtractor", "clean_text",
    
    # Models
    "TFIDFVectorizer", "CVJobMatcher", "MatchClassifier",
    
    # Crawlers
    "JobCrawler", "ITViecCrawler", "TopDevCrawler",
    
    # Utils
    "SkillDictionary",
]
