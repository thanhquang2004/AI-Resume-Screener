"""
Job Crawler - Crawl job postings from ITViec, TopDev, etc.
"""
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import uuid
import logging
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

from .base_crawler import BaseCrawler
from ..schemas.job import JobPosting, JobRequirements
from ..utils.skill_dictionary import SkillDictionary

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
        self.skill_dict = SkillDictionary()
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract technical skills from text using skill dictionary.
        
        Args:
            text: Job description or requirements text
            
        Returns:
            List of extracted and standardized skills
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Extract skills using skill dictionary
        extracted = self.skill_dict.extract_skills(text_lower)
        found_skills.update(extracted)
        
        return sorted(list(found_skills))
    
    def create_job_posting(self, data: Dict[str, Any]) -> JobPosting:
        """
        Create JobPosting from crawled data.
        
        Args:
            data: Crawled job data
            
        Returns:
            JobPosting object
        """
        job_id = data.get('job_id') or f"{self.source}_{uuid.uuid4().hex[:8]}"
        
        # Extract skills from requirements text and description
        requirements_text = data.get('requirements_text', '')
        description = data.get('description', '')
        
        # Auto-extract skills if not provided
        required_skills = data.get('required_skills', [])
        if not required_skills:
            combined_text = f"{requirements_text} {description}"
            required_skills = self.extract_skills_from_text(combined_text)
        
        return JobPosting(
            job_id=job_id,
            title=data.get('title', 'Unknown'),
            company_name=data.get('company_name', 'Unknown'),
            location=data.get('location'),
            description=description,
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
    
    Uses BeautifulSoup to parse HTML and extract job information.
    """
    
    BASE_URL = "https://itviec.com"
    JOBS_URL = "https://itviec.com/it-jobs"
    
    def __init__(self, **kwargs):
        # Force Selenium usage for ITViec (JavaScript-heavy site)
        kwargs['use_selenium'] = True
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
        
        try:
            # Initialize Selenium WebDriver
            self.init_driver()
            
            for page in range(1, pages + 1):
                # Build search URL
                params = {}
                if keywords:
                    params['q'] = ' '.join(keywords)
                if location:
                    params['locations'] = location
                params['page'] = page
                
                url = f"{self.JOBS_URL}?{urlencode(params)}" if params else self.JOBS_URL
                logger.info(f"Crawling page {page}: {url}")
                
                # Fetch page with Selenium
                self.driver.get(url)
                
                # Wait for job listings to load
                time.sleep(3)  # Wait for JavaScript to render
                
                # Scroll to load lazy content
                self.scroll_to_bottom(pause_time=1.0)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                
                # Find job listings - try multiple selectors
                job_elements = soup.find_all('div', class_=['job', 'job-item', 'itviec-job'])
                if not job_elements:
                    job_elements = soup.find_all('div', attrs={'data-job-id': True})
                if not job_elements:
                    job_elements = soup.select('.job-list .job')
                
                if not job_elements:
                    logger.warning(f"No job listings found on page {page}")
                    break
                
                logger.info(f"Found {len(job_elements)} jobs on page {page}")
                
                # Parse each job
                for job_elem in job_elements:
                    try:
                        job_data = self._parse_job_listing(job_elem, soup)
                        if job_data:
                            # Get detailed info if URL available
                            if job_data.get('source_url'):
                                detail_data = self._fetch_job_detail(job_data['source_url'])
                                job_data.update(detail_data)
                            
                            job = self.create_job_posting(job_data)
                            yield job
                            self.request_count += 1
                            
                            # Delay between jobs
                            self.random_delay()
                    except Exception as e:
                        logger.error(f"Error parsing job: {e}", exc_info=True)
                        continue
                
                # Delay between pages
                if page < pages:
                    self.random_delay()
        
        except Exception as e:
            logger.error(f"Error crawling ITViec: {e}", exc_info=True)
        finally:
            # Clean up WebDriver
            self.close_driver()
        
        logger.info(f"ITViec crawl complete. Total: {self.request_count}")
    
    def _parse_job_listing(self, job_elem, soup) -> Optional[Dict[str, Any]]:
        """Parse job listing from search results."""
        try:
            # Extract job title and link
            title_elem = job_elem.find('h3') or job_elem.find('a', class_='title')
            if not title_elem:
                title_elem = job_elem.find('a')
            
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            job_url = title_elem.get('href', '') if title_elem else ''
            if job_url and not job_url.startswith('http'):
                job_url = urljoin(self.BASE_URL, job_url)
            
            # Extract company name
            company_elem = job_elem.find('div', class_=['company', 'company-name']) or \
                          job_elem.find('span', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = job_elem.find('div', class_=['location', 'city']) or \
                           job_elem.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract salary if visible
            salary_elem = job_elem.find('div', class_=['salary', 'salary-label'])
            salary_text = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Extract job ID from URL or data attribute
            job_id = job_elem.get('data-job-id') or \
                    (job_url.split('/')[-1] if job_url else None)
            
            return {
                'job_id': job_id,
                'title': title,
                'company_name': company,
                'location': location,
                'salary_text': salary_text,
                'source_url': job_url,
            }
        except Exception as e:
            logger.error(f"Error parsing job listing: {e}")
            return None
    
    def _fetch_job_detail(self, url: str) -> Dict[str, Any]:
        """Fetch and parse job detail page."""
        try:
            logger.debug(f"Fetching job detail: {url}")
            
            # Use Selenium if available, otherwise fallback to requests
            if self.driver:
                self.driver.get(url)
                time.sleep(2)  # Wait for content to load
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
            else:
                response = requests.get(url, headers=self.get_headers(), timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract description
            desc_elem = soup.find('div', class_=['job-description', 'description', 'content'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract requirements
            req_elem = soup.find('div', class_=['requirements', 'job-requirements'])
            requirements = req_elem.get_text(strip=True) if req_elem else ""
            
            # Extract skills/tags
            skills = []
            skill_elems = soup.find_all('span', class_=['skill', 'tag', 'badge'])
            for skill_elem in skill_elems:
                skill = skill_elem.get_text(strip=True).lower()
                if skill:
                    skills.append(skill)
            
            # Extract salary if available
            salary_text = None
            salary_elem = soup.find('div', class_=['salary', 'salary-range'])
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
            
            # Extract experience requirement
            exp_years_min = None
            exp_pattern = r'(\d+)\+?\s*(?:year|năm|years)'
            if requirements or description:
                exp_match = re.search(exp_pattern, f"{requirements} {description}", re.IGNORECASE)
                if exp_match:
                    exp_years_min = int(exp_match.group(1))
            
            return {
                'description': description,
                'requirements_text': requirements,
                'required_skills': skills if skills else None,
                'salary_text': salary_text,
                'experience_years_min': exp_years_min,
            }
        except Exception as e:
            logger.error(f"Error fetching job detail {url}: {e}")
            return {}
    
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """Parse raw HTML/data into structured format."""
        # Implementation would parse Selenium elements
        return {}


class TopDevCrawler(JobCrawler):
    """
    Crawler for TopDev.vn job postings.
    
    TopDev has an API which makes crawling easier.
    """
    
    BASE_URL = "https://topdev.vn"
    API_URL = "https://api-ms.topdev.vn/search/user/v3/jobs"
    
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
        
        try:
            for page in range(1, pages + 1):
                # Build API request
                params = {
                    'page': page,
                    'limit': 20,  # Jobs per page
                }
                
                if keywords:
                    params['keyword'] = ' '.join(keywords)
                if location:
                    params['location'] = location
                
                logger.info(f"Fetching TopDev page {page}")
                
                # Call API
                response = requests.get(
                    self.API_URL,
                    params=params,
                    headers=self.get_headers(),
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract jobs from response
                jobs_data = data.get('data', {}).get('jobs', [])
                if not jobs_data:
                    logger.warning(f"No jobs found on page {page}")
                    break
                
                logger.info(f"Found {len(jobs_data)} jobs on page {page}")
                
                # Parse each job
                for job_raw in jobs_data:
                    try:
                        job_data = self.parse_item(job_raw)
                        if job_data:
                            job = self.create_job_posting(job_data)
                            yield job
                            self.request_count += 1
                    except Exception as e:
                        logger.error(f"Error parsing job: {e}", exc_info=True)
                        continue
                
                # Delay between pages
                if page < pages:
                    self.random_delay()
        
        except Exception as e:
            logger.error(f"Error crawling TopDev: {e}", exc_info=True)
        
        logger.info(f"TopDev crawl complete. Total: {self.request_count}")
    
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """Parse TopDev API response into structured format."""
        try:
            # Extract basic info
            job_id = str(raw_data.get('id'))
            title = raw_data.get('title', 'Unknown')
            
            # Company info
            company_data = raw_data.get('company', {})
            company_name = company_data.get('name', 'Unknown')
            
            # Location
            locations = raw_data.get('locations', [])
            location = locations[0].get('name') if locations else None
            
            # Skills
            skills_raw = raw_data.get('skills', [])
            required_skills = [s.get('name', '').lower() for s in skills_raw if s.get('name')]
            
            # Salary
            salary_text = raw_data.get('salaryText') or raw_data.get('salary')
            
            # URL
            slug = raw_data.get('slug', '')
            source_url = f"{self.BASE_URL}/{slug}" if slug else None
            
            # Description (may need separate API call for full details)
            description = raw_data.get('description', '')
            requirements = raw_data.get('requirements', '')
            
            # Experience
            exp_years_min = raw_data.get('experienceYearMin')
            exp_years_max = raw_data.get('experienceYearMax')
            
            # Benefits
            benefits = []
            benefits_raw = raw_data.get('benefits', [])
            if isinstance(benefits_raw, list):
                benefits = [b.get('name') for b in benefits_raw if isinstance(b, dict) and b.get('name')]
            
            return {
                'job_id': job_id,
                'title': title,
                'company_name': company_name,
                'location': location,
                'description': description,
                'requirements_text': requirements,
                'required_skills': required_skills,
                'salary_text': salary_text,
                'experience_years_min': exp_years_min,
                'experience_years_max': exp_years_max,
                'benefits': benefits,
                'source_url': source_url,
            }
        except Exception as e:
            logger.error(f"Error parsing TopDev job: {e}")
            return {}



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
