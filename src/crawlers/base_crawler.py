"""
Base Crawler - Abstract base class for web crawlers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
import time
import random
import logging

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    Abstract base class for web crawlers.
    Provides common functionality for rate limiting, error handling, etc.
    """
    
    def __init__(self,
                 delay_min: float = 2.0,
                 delay_max: float = 5.0,
                 max_retries: int = 3):
        """
        Initialize base crawler.
        
        Args:
            delay_min: Minimum delay between requests (seconds)
            delay_max: Maximum delay between requests (seconds)
            max_retries: Maximum retry attempts for failed requests
        """
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.request_count = 0
        self.error_count = 0
    
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
            raw_data: Raw data from web page
            
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
