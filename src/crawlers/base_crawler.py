"""
Base Crawler - Abstract base class for web crawlers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc  # Bypass Cloudflare bot detection

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    Abstract base class for web crawlers.
    Provides common functionality for rate limiting, error handling, etc.
    """
    
    def __init__(self,
                 delay_min: float = 2.0,
                 delay_max: float = 5.0,
                 max_retries: int = 3,
                 use_selenium: bool = False,
                 headless: bool = True):
        """
        Initialize base crawler.
        
        Args:
            delay_min: Minimum delay between requests (seconds)
            delay_max: Maximum delay between requests (seconds)
            max_retries: Maximum retry attempts for failed requests
            use_selenium: Whether to use Selenium WebDriver
            headless: Whether to run browser in headless mode
        """
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.request_count = 0
        self.error_count = 0
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
    
    @abstractmethod
    def crawl(self, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Crawl and yield items.
        
        Yields:
            Dict containing crawled data
        """
        pass
    
    @abstractmethod
    def parse_item(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw data into structured format.
        
        Args:
            raw_data: Raw data from web pagePerfect! Now let me create an .env file template and update the Dockerfile to install MySQL client:


            
        Returns:
            Parsed data dictionary
        """
        pass
    
    def random_delay(self):
        """Apply random delay between requests."""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with random User-Agent."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    def handle_error(self, error: Exception, url: str) -> bool:
        """
        Handle crawling error.
        
        Args:
            error: Exception that occurred
            url: URL that caused error
            
        Returns:
            True if should retry, False otherwise
        """
        self.error_count += 1
        logger.error(f"Error crawling {url}: {error}")
        
        if self.error_count <= self.max_retries:
            # Exponential backoff
            wait_time = (2 ** self.error_count) * 10
            logger.info(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return True
        
        return False
    
    def log_progress(self, current: int, total: Optional[int] = None):
        """Log crawling progress."""
        if total:
            logger.info(f"Progress: {current}/{total} ({current/total*100:.1f}%)")
        else:
            logger.info(f"Crawled: {current} items")
    
    def init_driver(self):
        """Initialize Selenium WebDriver with Cloudflare bypass."""
        if self.driver:
            return
        
        try:
            # Use undetected-chromedriver to bypass Cloudflare
            chrome_options = uc.ChromeOptions()
            
            if self.headless:
                chrome_options.add_argument('--headless=new')
            
            # Essential options for Docker stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Initialize undetected-chromedriver (bypasses Cloudflare)
            logger.info("Initializing undetected Chrome WebDriver (Cloudflare bypass)...")
            self.driver = uc.Chrome(
                options=chrome_options,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True,
                headless=self.headless,  # Pass headless to uc.Chrome
            )
            
            # Set timeouts for Cloudflare challenges (they can take 5-10 seconds)
            self.driver.set_page_load_timeout(60)  # 60 seconds for Cloudflare challenges
            self.driver.set_script_timeout(30)     # 30 seconds for scripts
            
            logger.info("✅ Undetected Chrome WebDriver initialized (Cloudflare bypass enabled)")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def scroll_to_bottom(self, pause_time: float = 1.0):
        """Scroll to bottom of page to load dynamic content."""
        if not self.driver:
            return
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
            # Calculate new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
