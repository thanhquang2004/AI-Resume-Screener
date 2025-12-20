"""
Job Crawler - Crawl job postings from ITViec, TopDev, etc.
"""
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import uuid
import logging
import json

from .base_crawler import BaseCrawler
from ..schemas.job import JobPosting, JobRequirements

logger = logging.getLogger(__name__)


class JobCrawler(BaseCrawler):
    """Base class for job posting crawlers."""
    
    def __init__(self, source: str, **kwargs):
        """
        Initialize job crawler.
        
        Args:
            source: Source website name
        """
        super().__init__(**kwargs)
        self.source = source
    
    def create_job_posting(self, data: Dict[str, Any]) -> JobPosting:
        """
        Create JobPosting from crawled data.
        
        Args:
            data: Crawled job data
            
        Returns:
            JobPosting object
        """
        job_id = data.get('job_id') or f"{self.source}_{uuid.uuid4().hex[:8]}"
        
        # Extract skills from requirements text
        requirements_text = data.get('requirements_text', '')
        required_skills = data.get('required_skills', [])
        
        return JobPosting(
            job_id=job_id,
            title=data.get('title', 'Unknown'),
            company_name=data.get('company_name', 'Unknown'),
            location=data.get('location'),
            description=data.get('description', ''),
            requirements_text=requirements_text,
            requirements=JobRequirements(
                required_skills=required_skills,
                experience_years_min=data.get('experience_years_min'),
                experience_years_max=data.get('experience_years_max'),
            ),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            salary_text=data.get('salary_text'),
            benefits=data.get('benefits', []),
            source=self.source,
            source_url=data.get('source_url'),
            crawled_at=datetime.now(),
        )


class ITViecCrawler(JobCrawler):
    """
    Crawler for ITViec.com job postings.
    
    Note: This is a stub implementation. Real implementation requires:
    - Selenium for JavaScript rendering
    - Actual CSS selectors from inspecting the website
    - Handle pagination and detail pages
    """
    
    BASE_URL = "https://itviec.com"
    JOBS_URL = "https://itviec.com/it-jobs"
    
    def __init__(self, **kwargs):
        super().__init__(source="itviec", **kwargs)
    
    def crawl(self, 
              keywords: Optional[List[str]] = None,
              location: Optional[str] = None,
              pages: int = 1) -> Generator[JobPosting, None, None]:
        """
        Crawl job postings from ITViec.
        
        Args:
            keywords: Search keywords
            location: Location filter
            pages: Number of pages to crawl
            
        Yields:
            JobPosting objects
        """
        logger.info(f"Starting ITViec crawl: keywords={keywords}, pages={pages}")
        
        # NOTE: This is a stub. Real implementation would:
        # 1. Use Selenium to render JavaScript
        # 2. Navigate to search page with keywords
        # 3. Extract job listings
        # 4. Visit each job detail page
        # 5. Parse and yield JobPosting
        
        # Example stub data for testing
        sample_jobs = [
            {
                "title": "Senior Python Developer",
                "company_name": "FPT Software",
                "location": "Hồ Chí Minh",
                "description": "We are looking for a Senior Python Developer...",
                "requirements_text": "5+ years experience with Python, Django, PostgreSQL. Knowledge of AWS, Docker preferred.",
                "required_skills": ["python", "django", "postgresql", "aws", "docker"],
                "experience_years_min": 5,
                "salary_text": "Up to $3000",
                "source_url": "https://itviec.com/it-jobs/senior-python-developer",
            },
            {
                "title": "Frontend Developer (React)",
                "company_name": "VNG Corporation",
                "location": "Hồ Chí Minh",
                "description": "Join our team as a Frontend Developer...",
                "requirements_text": "3+ years with React, TypeScript, CSS. Experience with Redux, testing.",
                "required_skills": ["react", "typescript", "css", "redux", "jest"],
                "experience_years_min": 3,
                "salary_text": "1500-2500 USD",
                "source_url": "https://itviec.com/it-jobs/frontend-developer-react",
            },
            {
                "title": "DevOps Engineer",
                "company_name": "Grab",
                "location": "Hồ Chí Minh",
                "description": "Build and maintain CI/CD pipelines...",
                "requirements_text": "Kubernetes, Docker, Terraform, AWS/GCP. Strong Linux skills.",
                "required_skills": ["kubernetes", "docker", "terraform", "aws", "linux", "cicd"],
                "experience_years_min": 4,
                "salary_text": "$2500-4000",
                "source_url": "https://itviec.com/it-jobs/devops-engineer",
            },
        ]
        
        for job_data in sample_jobs:
            self.random_delay()
            self.request_count += 1
            
            job = self.create_job_posting(job_data)
            yield job
        
        logger.info(f"ITViec crawl complete. Total: {self.request_count}")
    
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """Parse raw HTML/data into structured format."""
        # Implementation would parse Selenium elements
        return {}


class TopDevCrawler(JobCrawler):
    """
    Crawler for TopDev.vn job postings.
    
    TopDev has a public API which makes crawling easier.
    """
    
    BASE_URL = "https://topdev.vn"
    API_URL = "https://api.topdev.vn/td/v2/jobs"
    
    def __init__(self, **kwargs):
        super().__init__(source="topdev", **kwargs)
    
    def crawl(self,
              keywords: Optional[List[str]] = None,
              location: Optional[str] = None,
              pages: int = 1) -> Generator[JobPosting, None, None]:
        """
        Crawl job postings from TopDev API.
        
        Args:
            keywords: Search keywords
            location: Location filter
            pages: Number of pages to crawl
            
        Yields:
            JobPosting objects
        """
        logger.info(f"Starting TopDev crawl: keywords={keywords}, pages={pages}")
        
        # NOTE: Real implementation would call the API
        # import requests
        # response = requests.get(self.API_URL, params={...})
        # data = response.json()
        
        # Stub data for testing
        sample_jobs = [
            {
                "title": "Java Developer",
                "company_name": "Tiki",
                "location": "Hồ Chí Minh",
                "description": "Develop microservices for e-commerce platform...",
                "requirements_text": "Java, Spring Boot, Microservices, MySQL, Redis",
                "required_skills": ["java", "springboot", "microservices", "mysql", "redis"],
                "experience_years_min": 3,
                "salary_text": "20-35 triệu",
                "source_url": "https://topdev.vn/java-developer",
            },
            {
                "title": "Full Stack Developer",
                "company_name": "Shopee",
                "location": "Hồ Chí Minh",
                "description": "Build features for Shopee platform...",
                "requirements_text": "React, Node.js, MongoDB, AWS, Docker",
                "required_skills": ["react", "nodejs", "mongodb", "aws", "docker"],
                "experience_years_min": 2,
                "salary_text": "25-45 triệu",
                "source_url": "https://topdev.vn/fullstack-developer",
            },
            {
                "title": "Data Engineer",
                "company_name": "Momo",
                "location": "Hồ Chí Minh",
                "description": "Build data pipelines and ETL processes...",
                "requirements_text": "Python, Spark, Airflow, SQL, AWS",
                "required_skills": ["python", "spark", "airflow", "sql", "aws"],
                "experience_years_min": 3,
                "salary_text": "30-50 triệu",
                "source_url": "https://topdev.vn/data-engineer",
            },
        ]
        
        for job_data in sample_jobs:
            self.random_delay()
            self.request_count += 1
            
            job = self.create_job_posting(job_data)
            yield job
        
        logger.info(f"TopDev crawl complete. Total: {self.request_count}")
    
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """Parse API response into structured format."""
        # Parse TopDev API response format
        return {
            "title": raw_data.get("title"),
            "company_name": raw_data.get("company", {}).get("name"),
            "location": raw_data.get("locations", [{}])[0].get("name"),
            "description": raw_data.get("content"),
            "required_skills": [s.get("name") for s in raw_data.get("skills", [])],
            "source_url": raw_data.get("url"),
        }


def create_job_crawler(source: str) -> JobCrawler:
    """
    Factory function to create crawler.
    
    Args:
        source: Source name (itviec, topdev)
        
    Returns:
        JobCrawler instance
    """
    crawlers = {
        "itviec": ITViecCrawler,
        "topdev": TopDevCrawler,
    }
    
    if source.lower() not in crawlers:
        raise ValueError(f"Unknown source: {source}. Available: {list(crawlers.keys())}")
    
    return crawlers[source.lower()]()
