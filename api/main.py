"""
FastAPI Application - AI Resume Screener API
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers import CVParser
from src.preprocessing import SkillExtractor, clean_text
from src.models import CVJobMatcher
from src.schemas import (
    JobPosting, JobPostingCreate, JobRequirements,
    ExtractedCV, MatchResult, CompanyRanking, MatchCategory
)
from src.crawlers import ITViecCrawler, TopDevCrawler

# Initialize app
app = FastAPI(
    title="AI Resume Screener",
    description="API for matching CVs to Job postings and ranking companies",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
cv_parser = CVParser()
skill_extractor = SkillExtractor()
matcher = CVJobMatcher()

# In-memory storage (replace with database in production)
jobs_db: dict[str, JobPosting] = {}
cvs_db: dict[str, ExtractedCV] = {}


# Request/Response models
class JobInput(BaseModel):
    title: str
    company_name: str
    description: str
    requirements_text: str = ""
    required_skills: List[str] = []
    location: Optional[str] = None
    experience_years_min: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


class MatchRequest(BaseModel):
    cv_id: str
    job_ids: Optional[List[str]] = None
    top_n: int = 10


class HealthResponse(BaseModel):
    status: str
    version: str


# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# ===== CV Endpoints =====

@app.post("/api/v1/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload and parse a CV file (PDF or DOCX).
    
    Returns extracted information including skills, experience, education.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(400, f"Unsupported file type: {suffix}. Use PDF or DOCX.")
    
    try:
        # Read file
        content = await file.read()
        
        # Parse CV
        cv_data = cv_parser.parse_bytes(content, file.filename)
        extracted = cv_parser.extract_info(cv_data)
        
        # Store in memory
        cvs_db[extracted.cv_id] = extracted
        
        return {
            "cv_id": extracted.cv_id,
            "filename": file.filename,
            "name": extracted.name,
            "skills_found": len(extracted.all_skills),
            "skills": extracted.all_skills,
            "experience_years": extracted.total_experience_years,
            "highest_education": extracted.highest_education.value,
            "message": "CV processed successfully",
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to process CV: {str(e)}")


@app.get("/api/v1/cv/{cv_id}")
async def get_cv(cv_id: str):
    """Get extracted CV by ID."""
    if cv_id not in cvs_db:
        raise HTTPException(404, f"CV not found: {cv_id}")
    
    cv = cvs_db[cv_id]
    return cv.model_dump()


@app.get("/api/v1/cvs")
async def list_cvs():
    """List all uploaded CVs."""
    return {
        "count": len(cvs_db),
        "cvs": [
            {
                "cv_id": cv.cv_id,
                "name": cv.name,
                "skills_count": len(cv.all_skills),
            }
            for cv in cvs_db.values()
        ]
    }


# ===== Job Endpoints =====

@app.post("/api/v1/jobs")
async def create_job(job: JobInput):
    """Create a new job posting."""
    import uuid
    
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    # Extract skills if not provided
    skills = job.required_skills
    if not skills and job.requirements_text:
        skills = skill_extractor.extract(job.requirements_text)
    
    job_posting = JobPosting(
        job_id=job_id,
        title=job.title,
        company_name=job.company_name,
        description=job.description,
        requirements_text=job.requirements_text,
        requirements=JobRequirements(
            required_skills=skills,
            experience_years_min=job.experience_years_min,
        ),
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        source="manual",
    )
    
    jobs_db[job_id] = job_posting
    
    return {
        "job_id": job_id,
        "title": job.title,
        "company_name": job.company_name,
        "skills_extracted": skills,
        "message": "Job created successfully",
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job posting by ID."""
    if job_id not in jobs_db:
        raise HTTPException(404, f"Job not found: {job_id}")
    
    return jobs_db[job_id].model_dump()


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all job postings."""
    return {
        "count": len(jobs_db),
        "jobs": [
            {
                "job_id": job.job_id,
                "title": job.title,
                "company_name": job.company_name,
                "skills_count": len(job.requirements.required_skills),
            }
            for job in jobs_db.values()
        ]
    }


@app.post("/api/v1/jobs/crawl/{source}")
async def crawl_jobs(source: str, pages: int = 1):
    """
    Crawl jobs from a source (itviec, topdev).
    
    This uses stub data for demo purposes.
    """
    if source.lower() not in ["itviec", "topdev"]:
        raise HTTPException(400, f"Unknown source: {source}")
    
    crawler = ITViecCrawler() if source.lower() == "itviec" else TopDevCrawler()
    
    crawled = []
    for job in crawler.crawl(pages=pages):
        jobs_db[job.job_id] = job
        crawled.append({
            "job_id": job.job_id,
            "title": job.title,
            "company_name": job.company_name,
        })
    
    return {
        "source": source,
        "jobs_crawled": len(crawled),
        "jobs": crawled,
    }


# ===== Matching Endpoints =====

@app.post("/api/v1/match")
async def match_cv_to_jobs(request: MatchRequest):
    """
    Match a CV against job postings and return ranked companies.
    
    This is the main feature: for 1 CV, get a ranked list of potential companies.
    """
    # Get CV
    if request.cv_id not in cvs_db:
        raise HTTPException(404, f"CV not found: {request.cv_id}")
    
    cv = cvs_db[request.cv_id]
    
    # Get jobs to match against
    if request.job_ids:
        jobs = [jobs_db[jid] for jid in request.job_ids if jid in jobs_db]
        if not jobs:
            raise HTTPException(404, "No valid job IDs found")
    else:
        jobs = list(jobs_db.values())
        if not jobs:
            raise HTTPException(400, "No jobs in database. Add jobs first or use /api/v1/jobs/crawl")
    
    # Perform matching
    ranking = matcher.match_cv_to_jobs(cv, jobs, top_n=request.top_n)
    
    # Format response
    return {
        "cv_id": ranking.cv_id,
        "candidate_name": ranking.candidate_name,
        "candidate_skills": ranking.candidate_skills,
        "total_jobs_analyzed": ranking.total_jobs_analyzed,
        "summary": {
            "potential_count": ranking.potential_count,
            "review_needed_count": ranking.review_needed_count,
            "not_suitable_count": ranking.not_suitable_count,
        },
        "top_companies": ranking.top_companies,
        "common_skill_gaps": ranking.common_skill_gaps,
        "rankings": [
            {
                "rank": r.rank,
                "job_id": r.job_id,
                "title": r.job_title,
                "company_name": r.company_name,
                "score": r.score.overall_score,
                "category": r.score.category.value,
                "skill_score": r.score.skill_score,
                "matched_skills": r.gap_analysis.matched_skills,
                "missing_skills": r.gap_analysis.missing_skills,
                "recommendations": r.gap_analysis.recommendations,
            }
            for r in ranking.rankings
        ]
    }


@app.get("/api/v1/match/{cv_id}/{job_id}")
async def match_single(cv_id: str, job_id: str):
    """Match a specific CV against a specific job."""
    if cv_id not in cvs_db:
        raise HTTPException(404, f"CV not found: {cv_id}")
    if job_id not in jobs_db:
        raise HTTPException(404, f"Job not found: {job_id}")
    
    cv = cvs_db[cv_id]
    job = jobs_db[job_id]
    
    result = matcher.match(cv, job)
    
    return {
        "cv_id": result.cv_id,
        "job_id": result.job_id,
        "job_title": result.job_title,
        "company_name": result.company_name,
        "score": {
            "overall": result.score.overall_score,
            "category": result.score.category.value,
            "skill_score": result.score.skill_score,
            "experience_score": result.score.experience_score,
            "text_similarity": result.score.text_similarity,
        },
        "gap_analysis": {
            "matched_skills": result.gap_analysis.matched_skills,
            "missing_skills": result.gap_analysis.missing_skills,
            "extra_skills": result.gap_analysis.extra_skills,
            "skill_match_ratio": result.gap_analysis.skill_match_ratio,
            "recommendations": result.gap_analysis.recommendations,
        }
    }


# ===== Skills Endpoints =====

@app.post("/api/v1/skills/extract")
async def extract_skills(text: str = Form(...)):
    """Extract skills from text."""
    skills = skill_extractor.extract(text)
    categorized = skill_extractor.extract_with_context(text)
    
    return {
        "text_length": len(text),
        "skills_found": len(skills),
        "skills": skills,
        "categorized": categorized,
    }


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
