"""
Configuration settings for AI Resume Screener.
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    SKILL_DICT_PATH: Path = DATA_DIR / "skill_dictionaries" / "skills.json"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Crawler
    CRAWLER_DELAY_MIN: float = 2.0
    CRAWLER_DELAY_MAX: float = 5.0
    
    # Matching thresholds
    POTENTIAL_THRESHOLD: float = 0.75  # > 75% = Potential
    REVIEW_THRESHOLD: float = 0.50     # 50-75% = Review Needed
    
    # Database
    MYSQL_USER: str = "resume_user"
    MYSQL_PASSWORD: str = "resume_pass"
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "resume_screener"
    DATABASE_URL: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
