"""
FastAPI Application - AI Resume Screener API with MySQL Database
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
from pathlib import Path
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers import CVParser
from src.preprocessing import SkillExtractor
from src.models import CVJobMatcher
from src.schemas import (
    JobPosting, JobRequirements, JobLevel, JobType,
    ExtractedCV, MatchResult, CompanyRanking, MatchCategory
)
from src.crawlers import ITViecCrawler, TopDevCrawler
from src.database import get_db, init_db
from src.database.crud_cv import create_cv, get_cv as get_cv_db, get_all_cvs, cv_model_to_schema
from src.database.crud_job import create_job, get_job as get_job_db, get_all_jobs, job_model_to_schema
from src.database.crud_match import create_match_result, get_top_matches_for_cv, match_model_to_schema

# Initialize app
app = FastAPI(
    title="AI Resume Screener",
    description="API for matching CVs to Job postings with MySQL database",
    version="2.0.0",
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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


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


# ===== Health Check =====

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0", "database": "mysql"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check with database connection test."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "version": "2.0.0", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "version": "2.0.0", "database": f"error: {str(e)}"}


# ===== CV Endpoints =====

@app.post("/api/v1/cv/upload")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse a CV file (PDF or DOCX)."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(400, f"Unsupported file type: {suffix}. Use PDF or DOCX.")
    
    try:
        content = await file.read()
        cv_data = cv_parser.parse_bytes(content, file.filename)
        extracted = cv_parser.extract_info(cv_data)
        
        # Store in database
        create_cv(db, extracted)
        
        return {
            "cv_id": extracted.cv_id,
            "filename": file.filename,
            "name": extracted.name,
            "skills_found": len(extracted.all_skills),
            "skills": extracted.all_skills,
            "experience_years": extracted.total_experience_years,
            "highest_education": extracted.highest_education.value,
            "message": "CV processed and saved to database",
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to process CV: {str(e)}")


@app.get("/api/v1/cv/{cv_id}")
async def get_cv(cv_id: str, db: Session = Depends(get_db)):
    """Get extracted CV by ID."""
    db_cv = get_cv_db(db, cv_id)
    if not db_cv:
        raise HTTPException(404, f"CV not found: {cv_id}")
    
    cv = cv_model_to_schema(db_cv)
    return cv.model_dump()


@app.get("/api/v1/cvs")
async def list_cvs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all uploaded CVs."""
    db_cvs = get_all_cvs(db, skip, limit)
    
    return {
        "count": len(db_cvs),
        "cvs": [
            {
                "cv_id": cv.cv_id,
                "name": cv.name,
                "skills_count": len(cv.all_skills or []),
                "experience_years": cv.total_experience_years,
                "created_at": cv.created_at.isoformat() if cv.created_at else None,
            }
            for cv in db_cvs
        ]
    }


# ===== Job Endpoints =====

@app.post("/api/v1/jobs")
async def add_job(job_input: JobInput, db: Session = Depends(get_db)):
    """Add a new job posting manually."""
    job_id = f"manual_{uuid.uuid4().hex[:8]}"
    
    job_posting = JobPosting(
        job_id=job_id,
        title=job_input.title,
        company_name=job_input.company_name,
        description=job_input.description,
        requirements_text=job_input.requirements_text,
        requirements=JobRequirements(
            required_skills=job_input.required_skills,
            experience_years_min=job_input.experience_years_min,
        ),
        location=job_input.location,
        salary_min=job_input.salary_min,
        salary_max=job_input.salary_max,
        source="manual",
    )
    
    create_job(db, job_posting)
    
    return {
        "job_id": job_id,
        "message": "Job posting added successfully",
        "job": job_posting.model_dump(),
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job posting by ID."""
    db_job = get_job_db(db, job_id)
    if not db_job:
        raise HTTPException(404, f"Job not found: {job_id}")
    
    job = job_model_to_schema(db_job)
    return job.model_dump()


@app.get("/api/v1/jobs")
async def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all job postings."""
    db_jobs = get_all_jobs(db, skip, limit)
    
    return {
        "count": len(db_jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "title": job.title,
                "company_name": job.company_name,
                "location": job.location,
                "source": job.source,
                "required_skills": job.required_skills or [],
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in db_jobs
        ]
    }


@app.post("/api/v1/jobs/crawl/{source}")
async def crawl_jobs(
    source: str, 
    pages: int = 1, 
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Crawl jobs from a source (itviec, topdev).
    
    Args:
        source: Source website (itviec or topdev)
        pages: Number of pages to crawl (default: 1, max: 5)
        keywords: Search keywords (comma-separated)
        location: Location filter (e.g., "Ho Chi Minh", "Ha Noi")
        
    Note: This is a POST endpoint, not GET. Use:
        curl -X POST "http://localhost:8000/api/v1/jobs/crawl/itviec?pages=2&keywords=python"
    """
    if source.lower() not in ["itviec", "topdev"]:
        raise HTTPException(400, f"Unknown source: {source}. Available: itviec, topdev")
    
    # Limit pages to prevent very long requests
    if pages > 5:
        pages = 5
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Starting crawl: source={source}, pages={pages}, keywords={keywords}")
    
    try:
        # Parse keywords
        keyword_list = [k.strip() for k in keywords.split(',')] if keywords else None
        
        # Create crawler
        logger.info(f"Creating {source} crawler...")
        crawler = ITViecCrawler() if source.lower() == "itviec" else TopDevCrawler()
        
        # Crawl jobs
        crawled = []
        errors = []
        
        logger.info(f"Starting crawl iteration...")
        for idx, job in enumerate(crawler.crawl(keywords=keyword_list, location=location, pages=pages), 1):
            try:
                logger.info(f"Processing job {idx}: {job.title}")
                # Save to database
                create_job(db, job)
                crawled.append({
                    "job_id": job.job_id,
                    "title": job.title,
                    "company_name": job.company_name,
                    "location": job.location,
                    "skills": job.requirements.required_skills[:5] if job.requirements.required_skills else [],
                })
            except Exception as e:
                # Rollback on error to allow next job to be saved
                db.rollback()
                logger.error(f"Error saving job {idx}: {e}")
                errors.append({
                    "job_id": job.job_id,
                    "title": job.title,
                    "error": str(e)
                })
        
        logger.info(f"Crawl complete: {len(crawled)} jobs saved")
        
        return {
            "source": source,
            "pages_crawled": pages,
            "keywords": keyword_list,
            "location": location,
            "jobs_crawled": len(crawled),
            "jobs_saved": len(crawled),
            "errors": len(errors),
            "jobs": crawled[:20],  # First 20 jobs
            "message": f"Successfully crawled and saved {len(crawled)} jobs from {source}",
        }
    except Exception as e:
        logger.error(f"Crawling failed: {e}", exc_info=True)
        raise HTTPException(500, f"Crawling failed: {str(e)}")


# ===== Matching Endpoints =====

@app.post("/api/v1/match")
async def match_cv_to_jobs(request: MatchRequest, db: Session = Depends(get_db)):
    """Match a CV against job postings and return ranked companies."""
    # Get CV from database
    db_cv = get_cv_db(db, request.cv_id)
    if not db_cv:
        raise HTTPException(404, f"CV not found: {request.cv_id}")
    
    cv = cv_model_to_schema(db_cv)
    
    # Get jobs from database
    if request.job_ids:
        jobs = []
        for job_id in request.job_ids:
            db_job = get_job_db(db, job_id)
            if db_job:
                jobs.append(job_model_to_schema(db_job))
    else:
        db_jobs = get_all_jobs(db)
        jobs = [job_model_to_schema(job) for job in db_jobs]
    
    if not jobs:
        raise HTTPException(404, "No jobs found to match against")
    
    # Perform matching
    ranking = matcher.match_cv_to_jobs(cv, jobs, top_n=request.top_n)
    
    # Save match results to database
    for match_result in ranking.rankings:
        try:
            create_match_result(db, match_result)
        except Exception as e:
            print(f"Warning: Could not save match result: {e}")
    
    return ranking.model_dump()


@app.post("/api/v1/match/{cv_id}/{job_id}")
async def match_cv_to_specific_job(cv_id: str, job_id: str, db: Session = Depends(get_db)):
    """Match a specific CV to a specific job."""
    # Get CV
    db_cv = get_cv_db(db, cv_id)
    if not db_cv:
        raise HTTPException(404, f"CV not found: {cv_id}")
    
    # Get Job
    db_job = get_job_db(db, job_id)
    if not db_job:
        raise HTTPException(404, f"Job not found: {job_id}")
    
    cv = cv_model_to_schema(db_cv)
    job = job_model_to_schema(db_job)
    
    # Perform matching
    result = matcher.match(cv, job)
    
    # Save to database
    try:
        create_match_result(db, result)
    except Exception as e:
        print(f"Warning: Could not save match result: {e}")
    
    return result.model_dump()


@app.get("/api/v1/match/{cv_id}/top")
async def get_top_matches(cv_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get top matches for a CV from database."""
    db_matches = get_top_matches_for_cv(db, cv_id, limit)
    
    if not db_matches:
        raise HTTPException(404, f"No matches found for CV: {cv_id}")
    
    matches = []
    for db_match in db_matches:
        db_job = get_job_db(db, db_match.job_id)
        if db_job:
            match = match_model_to_schema(db_match, db_job.title, db_job.company_name)
            matches.append(match.model_dump())
    
    return {
        "cv_id": cv_id,
        "matches_found": len(matches),
        "top_matches": matches,
    }


# ===== Utility Endpoints =====

@app.post("/api/v1/skills/extract")
async def extract_skills(text: str):
    """Extract skills from arbitrary text."""
    skills = skill_extractor.extract(text)
    categorized = skill_extractor.extract_with_context(text)
    
    return {
        "skills_found": len(skills),
        "skills": skills,
        "categorized": categorized,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
