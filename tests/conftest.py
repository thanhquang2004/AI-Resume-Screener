"""
Test Configuration - Pytest fixtures and sample data.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ===== Sample Data Fixtures =====

@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """
    NGUYEN VAN A
    Email: nguyenvana@email.com
    Phone: 0901234567
    LinkedIn: linkedin.com/in/nguyenvana
    
    SUMMARY
    Experienced Full Stack Developer with 5 years of experience in web development.
    Proficient in Python, JavaScript, and cloud technologies.
    
    SKILLS
    Programming Languages: Python, JavaScript, TypeScript, Java
    Frameworks: Django, Flask, React, Node.js, Express
    Databases: PostgreSQL, MongoDB, Redis
    Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
    Tools: Git, Jenkins, Jira, Confluence
    
    EXPERIENCE
    
    Senior Software Engineer | FPT Software | 2021 - Present
    - Developed microservices using Python Django and FastAPI
    - Built React frontend applications with TypeScript
    - Deployed applications on AWS using Docker and Kubernetes
    - Led team of 3 junior developers
    
    Software Developer | VNG Corporation | 2019 - 2021
    - Developed RESTful APIs using Node.js and Express
    - Worked with PostgreSQL and Redis for data storage
    - Implemented CI/CD pipelines with Jenkins
    
    Junior Developer | Startup XYZ | 2018 - 2019
    - Built web applications using Python Flask
    - Created responsive UI with React
    
    EDUCATION
    Bachelor of Computer Science
    Ho Chi Minh City University of Technology | 2014 - 2018
    GPA: 3.5/4.0
    
    CERTIFICATIONS
    - AWS Certified Solutions Architect
    - Google Cloud Professional Data Engineer
    """


@pytest.fixture
def sample_job_description():
    """Sample JD text for testing."""
    return """
    Senior Python Developer - FPT Software
    
    We are looking for a Senior Python Developer to join our growing team.
    
    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of Django or FastAPI
    - Experience with PostgreSQL and Redis
    - Familiarity with Docker and Kubernetes
    - AWS experience is a plus
    - Good communication skills
    
    Nice to have:
    - Experience with React or Vue.js
    - Knowledge of machine learning
    - Agile/Scrum experience
    
    Benefits:
    - Competitive salary
    - 13th month salary
    - Health insurance
    - Training budget
    """


@pytest.fixture
def sample_skills_text():
    """Text with various skills for extraction testing."""
    return """
    Required skills: Python, Java, JavaScript, React.js, Node.js
    Database: PostgreSQL, MongoDB, Redis
    Cloud: AWS, GCP, Azure
    DevOps: Docker, Kubernetes, Jenkins, Terraform
    Other: Git, Agile, Scrum, REST API, GraphQL
    """


# ===== Parser Fixtures =====

@pytest.fixture
def cv_parser():
    """CVParser instance."""
    from src.parsers import CVParser
    return CVParser()


@pytest.fixture
def pdf_parser():
    """PDFParser instance."""
    from src.parsers import PDFParser
    return PDFParser()


@pytest.fixture
def docx_parser():
    """DocxParser instance."""
    from src.parsers import DocxParser
    return DocxParser()


# ===== Preprocessing Fixtures =====

@pytest.fixture
def text_cleaner():
    """TextCleaner instance."""
    from src.preprocessing import TextCleaner
    return TextCleaner()


@pytest.fixture
def skill_extractor():
    """SkillExtractor instance."""
    from src.preprocessing import SkillExtractor
    return SkillExtractor()


# ===== Model Fixtures =====

@pytest.fixture
def vectorizer():
    """TFIDFVectorizer instance."""
    from src.models import TFIDFVectorizer
    return TFIDFVectorizer()


@pytest.fixture
def matcher():
    """CVJobMatcher instance."""
    from src.models import CVJobMatcher
    return CVJobMatcher()


@pytest.fixture
def classifier():
    """MatchClassifier instance."""
    from src.models import MatchClassifier
    return MatchClassifier()


# ===== Schema Fixtures =====

@pytest.fixture
def sample_job_posting():
    """Sample JobPosting object."""
    from src.schemas import JobPosting, JobRequirements
    
    return JobPosting(
        job_id="test_job_001",
        title="Senior Python Developer",
        company_name="FPT Software",
        description="We are looking for a Senior Python Developer...",
        requirements_text="5+ years Python, Django, PostgreSQL, AWS",
        requirements=JobRequirements(
            required_skills=["python", "django", "postgresql", "aws", "docker"],
            nice_to_have_skills=["react", "kubernetes"],
            experience_years_min=5,
        ),
        location="Ho Chi Minh City",
        source="test",
    )


@pytest.fixture
def sample_extracted_cv():
    """Sample ExtractedCV object."""
    from src.schemas import ExtractedCV, Education, Experience, EducationLevel
    from datetime import date
    
    return ExtractedCV(
        cv_id="test_cv_001",
        raw_text="Sample CV text...",
        name="Nguyen Van A",
        email="nguyenvana@email.com",
        phone="0901234567",
        skills=[
            {"name": "python", "category": "programming"},
            {"name": "django", "category": "framework"},
            {"name": "react", "category": "framework"},
            {"name": "postgresql", "category": "database"},
            {"name": "aws", "category": "cloud"},
            {"name": "docker", "category": "devops"},
        ],
        experience=[
            Experience(
                title="Senior Software Engineer",
                company="FPT Software",
                start_date=date(2021, 1, 1),
                end_date=None,
                description="Developed microservices with Python",
            ),
            Experience(
                title="Software Developer",
                company="VNG Corporation",
                start_date=date(2019, 1, 1),
                end_date=date(2020, 12, 31),
                description="Built APIs with Node.js",
            ),
        ],
        education=[
            Education(
                degree="Bachelor",
                field="Computer Science",
                institution="HCMUT",
                graduation_year=2018,
            )
        ],
    )
