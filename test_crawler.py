#!/usr/bin/env python3
"""
Test script for Selenium-based job crawlers.
Run this to test crawling functionality before deploying.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.crawlers import ITViecCrawler, TopDevCrawler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_itviec_crawler():
    """Test ITViec crawler with Selenium."""
    print("\n" + "="*60)
    print("Testing ITViec Crawler (Selenium)")
    print("="*60 + "\n")
    
    try:
        crawler = ITViecCrawler(headless=True)  # Set False to see browser
        
        # Crawl first page only
        jobs = list(crawler.crawl(pages=1))
        
        print(f"\n✅ Successfully crawled {len(jobs)} jobs from ITViec\n")
        
        # Display first 3 jobs
        for i, job in enumerate(jobs[:3], 1):
            print(f"Job #{i}:")
            print(f"  Title: {job.title}")
            print(f"  Company: {job.company_name}")
            print(f"  Location: {job.location}")
            print(f"  Skills: {', '.join(job.requirements.required_skills[:5])}")
            print(f"  URL: {job.source_url}")
            print()
        
        return True
    except Exception as e:
        print(f"\n❌ ITViec crawler failed: {e}\n")
        logger.exception("ITViec crawler error")
        return False


def test_topdev_crawler():
    """Test TopDev crawler (API-based, no Selenium needed)."""
    print("\n" + "="*60)
    print("Testing TopDev Crawler (API)")
    print("="*60 + "\n")
    
    try:
        crawler = TopDevCrawler()
        
        # Crawl first page only
        jobs = list(crawler.crawl(pages=1))
        
        print(f"\n✅ Successfully crawled {len(jobs)} jobs from TopDev\n")
        
        # Display first 3 jobs
        for i, job in enumerate(jobs[:3], 1):
            print(f"Job #{i}:")
            print(f"  Title: {job.title}")
            print(f"  Company: {job.company_name}")
            print(f"  Location: {job.location}")
            print(f"  Skills: {', '.join(job.requirements.required_skills[:5])}")
            print(f"  URL: {job.source_url}")
            print()
        
        return True
    except Exception as e:
        print(f"\n❌ TopDev crawler failed: {e}\n")
        logger.exception("TopDev crawler error")
        return False


if __name__ == "__main__":
    print("\n🚀 AI Resume Screener - Crawler Test\n")
    
    results = {
        "ITViec": test_itviec_crawler(),
        "TopDev": test_topdev_crawler(),
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    for source, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{source:20s} {status}")
    print("="*60 + "\n")
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)
