"""
Job Crawler - Crawl job postings from ITViec, TopDev, etc.
"""
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import uuid
import logging
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

# Playwright for Cloudflare bypass
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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
        
        # Simple pattern matching for common IT skills
        # Use word boundaries to match whole words
        skill_patterns = [
            # Programming languages
            r'\b(python|java|javascript|typescript|csharp|c\+\+|golang|go|rust|ruby|php|swift|kotlin|scala)\b',
            # Web frameworks
            r'\b(react|vue|angular|django|flask|fastapi|spring|springboot|rails|laravel|nodejs|express|nestjs|nextjs)\b',
            # Databases
            r'\b(mysql|postgresql|postgres|mongodb|redis|elasticsearch|oracle|sqlserver|sqlite)\b',
            # Cloud & DevOps
            r'\b(aws|azure|gcp|docker|kubernetes|k8s|terraform|jenkins|gitlab|github|cicd|ci/cd)\b',
            # Tools & Others
            r'\b(git|linux|unix|restapi|rest|api|graphql|microservices|agile|scrum)\b',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            found_skills.update(matches)
        
        # Normalize skills using skill dictionary
        normalized_skills = set()
        for skill in found_skills:
            normalized = self.skill_dict.normalize(skill)
            normalized_skills.add(normalized)
        
        return sorted(list(normalized_skills))
    
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
    
    Uses Playwright to bypass Cloudflare protection.
    Runs Playwright in a thread to avoid asyncio conflicts with FastAPI.
    """
    
    BASE_URL = "https://itviec.com"
    JOBS_URL = "https://itviec.com/it-jobs"
    
    def __init__(self, **kwargs):
        # Don't use Selenium - use Playwright for Cloudflare bypass
        kwargs['use_selenium'] = False
        super().__init__(source="itviec", **kwargs)
        self.browser = None
        self.playwright = None
        self._playwright_context = None
    
    def _run_playwright_crawl(self, keywords, location, pages):
        """
        Run Playwright crawl in a separate thread to avoid asyncio conflicts.
        Returns a list of JobPosting objects.
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Run: pip install playwright && playwright install chromium")
        
        from playwright.sync_api import sync_playwright
        
        jobs = []
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            logger.info("✅ Playwright browser initialized in thread")
            
            try:
                for page_num in range(1, pages + 1):
                    # Build search URL
                    params = {}
                    if keywords:
                        params['q'] = ' '.join(keywords)
                    if location:
                        params['locations'] = location
                    params['page'] = page_num
                    
                    url = f"{self.JOBS_URL}?{urlencode(params)}" if params else self.JOBS_URL
                    logger.info(f"Crawling page {page_num}: {url}")
                    
                    # Fetch page with Playwright
                    html_content = self._get_page_content_with_browser(browser, url)
                    if not html_content:
                        logger.error(f"Failed to fetch page {page_num}")
                        continue
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'lxml')
                    
                    # Save HTML for debugging
                    try:
                        with open(f'/tmp/itviec_page{page_num}.html', 'w') as f:
                            f.write(html_content)
                    except:
                        pass
                    
                    # Find job cards (they have 'job-card' in class)
                    job_cards = soup.find_all('div', class_=lambda x: x and 'job-card' in str(x))
                    logger.info(f"Found {len(job_cards)} job cards on page {page_num}")
                    
                    if not job_cards:
                        logger.warning("No job cards found. Checking for Cloudflare block...")
                        text_sample = soup.get_text()[:500]
                        logger.warning(f"Page text: {text_sample}")
                        continue
                    
                    # Parse each job card
                    for idx, card in enumerate(job_cards, 1):
                        try:
                            job_data = self._parse_job_card(card)
                            if job_data:
                                logger.info(f"Parsed job {idx}: {job_data.get('title')} at {job_data.get('company_name')}")
                                
                                # Skip detail page fetching for faster crawling
                                # (Each detail page takes 20+ seconds due to Cloudflare)
                                # Uncomment below to fetch full descriptions:
                                # if job_data.get('source_url'):
                                #     detail_data = self._fetch_job_detail_with_browser(browser, job_data['source_url'])
                                #     if detail_data:
                                #         job_data.update(detail_data)
                                
                                job = self.create_job_posting(job_data)
                                jobs.append(job)
                                self.request_count += 1
                                
                                # Small delay between jobs
                                time.sleep(0.5)
                        except Exception as e:
                            logger.error(f"Error parsing job {idx}: {e}")
                            continue
                    
                    # Delay between pages
                    if page_num < pages:
                        time.sleep(3.0)
            finally:
                browser.close()
        
        return jobs
    
    def _get_page_content_with_browser(self, browser, url: str) -> Optional[str]:
        """Fetch page content using an existing Playwright browser."""
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh',
        )
        
        # Add stealth scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for Cloudflare challenge (up to 20 seconds)
            for i in range(4):
                time.sleep(5)
                if "Just a moment" not in page.title() and "Chờ" not in page.title():
                    break
            
            content = page.content()
            return content
        except Exception as e:
            logger.error(f"Playwright error fetching {url}: {e}")
            return None
        finally:
            context.close()
    
    def _fetch_job_detail_with_browser(self, browser, url: str) -> Optional[Dict[str, Any]]:
        """Fetch job detail page using an existing Playwright browser."""
        try:
            logger.info(f"Fetching detail page: {url[:80]}...")
            html_content = self._get_page_content_with_browser(browser, url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Description - look for div with description-related class
            description = ""
            desc_div = soup.find('div', class_=lambda x: x and 'description' in str(x).lower())
            if desc_div:
                description = desc_div.get_text(strip=True)
            
            # Also try common containers
            if not description:
                for selector in ['#job-description', '.job-description', '.job-detail', '.job-content']:
                    elem = soup.select_one(selector)
                    if elem:
                        description = elem.get_text(strip=True)
                        break
            
            # Requirements - usually in a section
            requirements = ""
            req_section = soup.find(string=lambda x: x and 'requirement' in str(x).lower())
            if req_section:
                parent = req_section.find_parent('div')
                if parent:
                    requirements = parent.get_text(strip=True)
            
            # Salary
            salary_text = None
            salary_elem = soup.find(class_=lambda x: x and 'salary' in str(x).lower())
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
            
            return {
                'description': description[:5000] if description else "",
                'requirements_text': requirements[:3000] if requirements else "",
                'salary_text': salary_text,
            }
        except Exception as e:
            logger.error(f"Error fetching job detail: {e}")
            return None

    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw data into structured format.
        For ITViec, this is handled by _parse_job_card.
        """
        # ITViec uses _parse_job_card for job card parsing
        if isinstance(raw_data, dict):
            return raw_data
        return {}
    
    def crawl(self, 
              keywords: Optional[List[str]] = None,
              location: Optional[str] = None,
              pages: int = 1) -> Generator[JobPosting, None, None]:
        """
        Crawl job postings from ITViec using Playwright (bypasses Cloudflare).
        Runs Playwright in a thread pool to avoid asyncio conflicts.
        
        Args:
            keywords: Search keywords
            location: Location filter
            pages: Number of pages to crawl
            
        Yields:
            JobPosting objects
        """
        logger.info(f"Starting ITViec crawl with Playwright: keywords={keywords}, pages={pages}")
        
        import concurrent.futures
        
        try:
            # Run Playwright in a separate thread to avoid asyncio conflict
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_playwright_crawl, keywords, location, pages)
                jobs = future.result(timeout=600)  # 10 minute timeout
                
                for job in jobs:
                    yield job
        
        except Exception as e:
            logger.error(f"Error crawling ITViec: {e}", exc_info=True)
        
        logger.info(f"ITViec crawl complete. Total: {self.request_count}")
    
    def _parse_job_card(self, card) -> Optional[Dict[str, Any]]:
        """Parse a job card from ITViec listing page."""
        try:
            # Title from h3
            title_elem = card.find('h3')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Company from link to /companies/ or span with text-hover-underline
            company = ""
            company_link = card.find('a', href=lambda x: x and '/companies/' in str(x))
            if company_link:
                company = company_link.get_text(strip=True)
            
            # Also try span with text-hover-underline class (common pattern for company names)
            if not company:
                company_span = card.find('span', class_=lambda x: x and 'text-hover-underline' in str(x))
                if company_span:
                    company = company_span.get_text(strip=True)
            
            # Also try any span inside a link to companies
            if not company:
                for link in card.find_all('a'):
                    href = link.get('href', '')
                    if '/companies/' in href:
                        company = link.get_text(strip=True)
                        break
            
            # Job URL - get from sign_in link which contains job slug
            job_url = None
            sign_in_link = card.find('a', href=lambda x: x and '/sign_in?job=' in str(x))
            if sign_in_link:
                href = sign_in_link.get('href', '')
                # Extract job slug from /sign_in?job=job-slug-here
                import urllib.parse
                parsed = urllib.parse.urlparse(href)
                params = urllib.parse.parse_qs(parsed.query)
                job_slug = params.get('job', [''])[0]
                if job_slug:
                    job_url = f"{self.BASE_URL}/it-jobs/{job_slug}"
            
            # Also check for direct job link
            if not job_url:
                job_link = card.find('a', href=lambda x: x and '/it-jobs/' in str(x) and len(str(x)) > 30)
                if job_link:
                    href = job_link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.BASE_URL, href)
                    job_url = href
            
            # Location
            location = None
            location_text = card.find(string=lambda x: x and ('Ho Chi Minh' in str(x) or 'Ha Noi' in str(x) or 'Da Nang' in str(x)))
            if location_text:
                location = str(location_text).strip()
            
            # Skills from tags
            skills = []
            skill_links = card.find_all('a', href=lambda x: x and '/it-jobs/' in str(x) and 'click_source=Skill' in str(x))
            for skill_link in skill_links:
                skill = skill_link.get_text(strip=True)
                if skill and len(skill) < 30:
                    skills.append(skill)
            
            return {
                'title': title,
                'company_name': company,
                'location': location,
                'source_url': job_url,
                'required_skills': skills,
            }
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None


class TopDevCrawler(JobCrawler):
    """
    Crawler for TopDev.vn job postings.
    
    Uses Playwright to scrape TopDev's Next.js website.
    TopDev embeds job data as JSON in script tags, which we extract.
    """
    
    BASE_URL = "https://topdev.vn"
    SEARCH_URL = "https://topdev.vn/jobs/search"
    
    def __init__(self, **kwargs):
        super().__init__(source="topdev", **kwargs)
    
    def crawl(self,
              keywords: Optional[List[str]] = None,
              location: Optional[str] = None,
              pages: int = 1) -> Generator[JobPosting, None, None]:
        """
        Crawl job postings from TopDev using Playwright.
        
        Args:
            keywords: Search keywords
            location: Location filter  
            pages: Number of pages to crawl
            
        Yields:
            JobPosting objects
        """
        logger.info(f"Starting TopDev crawl: keywords={keywords}, pages={pages}")
        
        # Use ThreadPoolExecutor to run Playwright in separate thread
        from concurrent.futures import ThreadPoolExecutor
        import json
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self._run_playwright_crawl,
                keywords,
                location,
                pages
            )
            jobs_data = future.result()
        
        # Yield jobs from collected data
        for job_data in jobs_data:
            try:
                job = self.create_job_posting(job_data)
                yield job
                self.request_count += 1
            except Exception as e:
                logger.error(f"Error creating job posting: {e}")
                continue
        
        logger.info(f"TopDev crawl complete. Total: {self.request_count}")
    
    def _run_playwright_crawl(self,
                               keywords: Optional[List[str]],
                               location: Optional[str],
                               pages: int) -> List[Dict[str, Any]]:
        """Run Playwright crawl in sync context."""
        from playwright.sync_api import sync_playwright
        import json
        import re
        
        all_jobs = []
        seen_ids = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            try:
                for page_num in range(1, pages + 1):
                    # Build URL with parameters
                    url = self.SEARCH_URL
                    params = []
                    if keywords:
                        params.append(f"keyword={'+'.join(keywords)}")
                    if location:
                        # Map location names to region IDs
                        location_map = {
                            'ho chi minh': '79',
                            'hcm': '79',
                            'ha noi': '01',
                            'hanoi': '01',
                            'da nang': '048',
                            'danang': '048',
                        }
                        region_id = location_map.get(location.lower().replace(' ', ''), '')
                        if region_id:
                            params.append(f"region_ids={region_id}")
                    if page_num > 1:
                        params.append(f"page={page_num}")
                    
                    if params:
                        url = f"{url}?{'&'.join(params)}"
                    
                    logger.info(f"Fetching TopDev page {page_num}: {url}")
                    
                    # Load page with longer timeout
                    page.goto(url, wait_until='networkidle', timeout=60000)
                    time.sleep(3)  # Wait for JS hydration
                    
                    # Extract job data from Next.js script tags
                    content = page.content()
                    jobs_on_page = self._extract_jobs_from_html(content, seen_ids)
                    
                    if not jobs_on_page:
                        logger.warning(f"No jobs found on page {page_num}")
                        # Try extracting from visible cards as fallback
                        jobs_on_page = self._extract_jobs_from_cards(page, seen_ids)
                    
                    logger.info(f"Found {len(jobs_on_page)} jobs on page {page_num}")
                    all_jobs.extend(jobs_on_page)
                    
                    # Delay between pages
                    if page_num < pages:
                        time.sleep(random.uniform(2, 4))
                        
            except Exception as e:
                logger.error(f"Error in Playwright crawl: {e}", exc_info=True)
            finally:
                browser.close()
        
        return all_jobs
    
    def _extract_jobs_from_html(self, html_content: str, seen_ids: set) -> List[Dict[str, Any]]:
        """Extract job data from Next.js hydration scripts."""
        import re
        import json
        
        jobs = []
        
        # Find all job entries in the script data
        # Pattern: "id":2081152,"title":"..."
        job_pattern = re.compile(
            r'\\"id\\":(\d{7}),\\"title\\":\\"([^\\]+)\\".*?' +
            r'\\"display_name\\":\\"([^\\]*)\\".*?' +
            r'(?:\\"skills_str\\":\\"([^\\]*)\\")?.*?' +
            r'(?:\\"address_region_list\\":\\"([^\\]*)\\")?.*?' +
            r'(?:\\"detail_url\\":\\"([^\\]*)\\")?',
            re.DOTALL
        )
        
        # Alternative: Extract JSON blocks for jobs
        # Look for job objects with id in 2000000+ range
        for match in re.finditer(r'\\"id\\":(\d{7}),\\"title\\":\\"([^\\]+)\\"', html_content):
            job_id = match.group(1)
            title = match.group(2)
            
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            
            # Try to extract more data around this match
            start = max(0, match.start() - 50)
            end = min(len(html_content), match.end() + 2000)
            context = html_content[start:end]
            
            # Extract company name
            company_match = re.search(r'\\"display_name\\":\\"([^\\]+)\\"', context)
            company_name = company_match.group(1) if company_match else 'Unknown'
            
            # Extract skills
            skills_match = re.search(r'\\"skills_str\\":\\"([^\\]*)\\"', context)
            skills_str = skills_match.group(1) if skills_match else ''
            skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
            
            # Extract location
            location_match = re.search(r'\\"address_region_list\\":\\"([^\\]*)\\"', context)
            location = location_match.group(1) if location_match else None
            
            # Extract URL
            url_match = re.search(r'\\"detail_url\\":\\"([^\\]*)\\"', context)
            source_url = url_match.group(1).replace('\\/', '/') if url_match else None
            
            # Extract salary
            salary_match = re.search(r'\\"value\\":\\"([^\\]+)\\"', context)
            salary_text = salary_match.group(1) if salary_match else None
            if salary_text == 'Negotiable':
                salary_text = None
            
            jobs.append({
                'job_id': job_id,
                'title': title,
                'company_name': company_name,
                'location': location,
                'required_skills': skills,
                'source_url': source_url,
                'salary_text': salary_text,
            })
        
        return jobs
    
    def _extract_jobs_from_cards(self, page, seen_ids: set) -> List[Dict[str, Any]]:
        """Fallback: Extract jobs from visible job cards."""
        from bs4 import BeautifulSoup
        
        jobs = []
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for job card elements
        job_cards = soup.find_all('a', href=re.compile(r'/detail-jobs/'))
        
        for card in job_cards:
            try:
                href = card.get('href', '')
                if not href or 'detail-jobs' not in href:
                    continue
                
                # Extract job ID from URL
                id_match = re.search(r'-(\d{7})$', href)
                if not id_match:
                    continue
                job_id = id_match.group(1)
                
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                
                # Extract title
                title_elem = card.find(['h3', 'h4', 'span'], class_=lambda x: x and 'title' in x.lower() if x else False)
                title = title_elem.get_text(strip=True) if title_elem else card.get_text(strip=True)[:100]
                
                jobs.append({
                    'job_id': job_id,
                    'title': title,
                    'company_name': 'Unknown',
                    'source_url': f"{self.BASE_URL}{href}" if href.startswith('/') else href,
                })
            except Exception as e:
                logger.error(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """Parse raw job data into structured format."""
        # Data is already structured from extraction methods
        return raw_data if isinstance(raw_data, dict) else {}



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
