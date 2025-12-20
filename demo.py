"""
Demo Script - AI Resume Screener
Demonstrates the main workflow: Upload CV → Match Jobs → Get Rankings
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers import CVParser
from src.preprocessing import SkillExtractor
from src.models import CVJobMatcher
from src.schemas import (
    CVData, ExtractedCV, Education, Experience,
    JobPosting, JobRequirements, EducationLevel
)
from src.crawlers import ITViecCrawler, TopDevCrawler
from datetime import date


def create_sample_cv() -> ExtractedCV:
    """Create a sample CV for demo."""
    return ExtractedCV(
        cv_id="demo_cv_001",
        raw_text="""
        NGUYEN VAN A
        Senior Python Developer
        Email: nguyenvana@email.com
        
        SKILLS
        Python, Django, FastAPI, PostgreSQL, Redis
        React, TypeScript, Docker, Kubernetes, AWS
        
        EXPERIENCE
        Senior Developer at FPT Software (2021-Present)
        - Built microservices with Python and FastAPI
        - Deployed on AWS using Docker and Kubernetes
        
        Developer at VNG (2019-2021)
        - Developed APIs with Django
        - Worked with PostgreSQL and Redis
        
        EDUCATION
        Bachelor of Computer Science, HCMUT, 2018
        """,
        name="Nguyen Van A",
        email="nguyenvana@email.com",
        skills=[
            {"name": "python", "category": "programming"},
            {"name": "django", "category": "framework"},
            {"name": "fastapi", "category": "framework"},
            {"name": "postgresql", "category": "database"},
            {"name": "redis", "category": "database"},
            {"name": "react", "category": "framework"},
            {"name": "typescript", "category": "programming"},
            {"name": "docker", "category": "devops"},
            {"name": "kubernetes", "category": "devops"},
            {"name": "aws", "category": "cloud"},
        ],
        experience=[
            Experience(
                title="Senior Developer",
                company="FPT Software",
                start_date=date(2021, 1, 1),
                description="Built microservices with Python"
            ),
            Experience(
                title="Developer",
                company="VNG",
                start_date=date(2019, 1, 1),
                end_date=date(2020, 12, 31),
                description="Developed APIs with Django"
            ),
        ],
        education=[
            Education(
                degree="Bachelor",
                field="Computer Science",
                institution="HCMUT",
                graduation_year=2018
            )
        ],
    )


def create_sample_jobs() -> list[JobPosting]:
    """Create sample job postings for demo."""
    return [
        JobPosting(
            job_id="job_001",
            title="Senior Python Developer",
            company_name="FPT Software",
            location="Ho Chi Minh City",
            description="Looking for Senior Python Developer to build microservices",
            requirements_text="5+ years Python, Django/FastAPI, PostgreSQL, Docker, AWS",
            requirements=JobRequirements(
                required_skills=["python", "django", "postgresql", "docker", "aws"],
                nice_to_have_skills=["kubernetes", "redis"],
                experience_years_min=5,
            ),
            salary_text="Up to $3500",
            source="demo",
        ),
        JobPosting(
            job_id="job_002",
            title="Full Stack Developer",
            company_name="VNG Corporation",
            location="Ho Chi Minh City",
            description="Full Stack role working on Zalo features",
            requirements_text="React, Node.js, TypeScript, MongoDB, AWS",
            requirements=JobRequirements(
                required_skills=["react", "nodejs", "typescript", "mongodb", "aws"],
                experience_years_min=3,
            ),
            salary_text="$2000-3000",
            source="demo",
        ),
        JobPosting(
            job_id="job_003",
            title="DevOps Engineer",
            company_name="Grab",
            location="Ho Chi Minh City",
            description="DevOps role for infrastructure automation",
            requirements_text="Kubernetes, Docker, Terraform, AWS/GCP, Python scripting",
            requirements=JobRequirements(
                required_skills=["kubernetes", "docker", "terraform", "aws", "python"],
                nice_to_have_skills=["golang", "jenkins"],
                experience_years_min=4,
            ),
            salary_text="$3000-5000",
            source="demo",
        ),
        JobPosting(
            job_id="job_004",
            title="Backend Engineer",
            company_name="Shopee",
            location="Ho Chi Minh City",
            description="Backend development for e-commerce platform",
            requirements_text="Java, Spring Boot, MySQL, Redis, Kafka",
            requirements=JobRequirements(
                required_skills=["java", "springboot", "mysql", "redis", "kafka"],
                experience_years_min=3,
            ),
            salary_text="$2500-4000",
            source="demo",
        ),
        JobPosting(
            job_id="job_005",
            title="Data Engineer",
            company_name="Momo",
            location="Ho Chi Minh City",
            description="Build data pipelines for fintech analytics",
            requirements_text="Python, Spark, Airflow, SQL, AWS",
            requirements=JobRequirements(
                required_skills=["python", "spark", "airflow", "sql", "aws"],
                nice_to_have_skills=["kafka", "mongodb"],
                experience_years_min=3,
            ),
            salary_text="$2500-4000",
            source="demo",
        ),
        JobPosting(
            job_id="job_006",
            title="Frontend Developer",
            company_name="Tiki",
            location="Ho Chi Minh City",
            description="React developer for e-commerce frontend",
            requirements_text="React, TypeScript, Redux, CSS, Jest",
            requirements=JobRequirements(
                required_skills=["react", "typescript", "redux", "css"],
                nice_to_have_skills=["nextjs", "graphql"],
                experience_years_min=2,
            ),
            salary_text="$1500-2500",
            source="demo",
        ),
    ]


def print_separator():
    print("\n" + "=" * 70 + "\n")


def main():
    print_separator()
    print("🎯 AI Resume Screener - Demo")
    print("   Matching CV with Job Postings")
    print_separator()
    
    # 1. Create sample CV
    print("📄 Loading sample CV...")
    cv = create_sample_cv()
    print(f"   Candidate: {cv.name}")
    print(f"   Skills: {', '.join(cv.all_skills)}")
    print(f"   Experience: {cv.total_experience_years} years")
    print(f"   Education: {cv.highest_education.value}")
    
    print_separator()
    
    # 2. Create sample jobs
    print("📋 Loading job postings...")
    jobs = create_sample_jobs()
    for job in jobs:
        print(f"   - {job.title} @ {job.company_name}")
    
    print_separator()
    
    # 3. Initialize matcher
    print("🔄 Initializing CV-Job Matcher...")
    matcher = CVJobMatcher()
    
    # 4. Match CV to all jobs
    print("🎯 Matching CV against all jobs...")
    ranking = matcher.match_cv_to_jobs(cv, jobs)
    
    print_separator()
    
    # 5. Display results
    print(f"📊 RANKING RESULTS FOR: {ranking.candidate_name}")
    print(f"   Total jobs analyzed: {ranking.total_jobs_analyzed}")
    print(f"   Potential matches: {ranking.potential_count}")
    print(f"   Need review: {ranking.review_needed_count}")
    print(f"   Not suitable: {ranking.not_suitable_count}")
    
    print_separator()
    
    print("🏆 TOP MATCHING COMPANIES (High → Low):\n")
    
    for r in ranking.rankings:
        # Category emoji
        if r.score.category.value == "POTENTIAL":
            emoji = "🟢"
        elif r.score.category.value == "REVIEW_NEEDED":
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        print(f"#{r.rank} {emoji} {r.company_name}")
        print(f"   Position: {r.job_title}")
        print(f"   Score: {r.score.overall_score*100:.0f}% ({r.score.category.value})")
        print(f"   Skill Match: {r.score.skill_score*100:.0f}%")
        
        # Gap analysis
        if r.gap_analysis.matched_skills:
            print(f"   ✅ Matched: {', '.join(r.gap_analysis.matched_skills[:5])}")
        if r.gap_analysis.missing_skills:
            print(f"   ❌ Missing: {', '.join(r.gap_analysis.missing_skills[:5])}")
        
        # Recommendations
        if r.gap_analysis.recommendations:
            print(f"   💡 Tip: {r.gap_analysis.recommendations[0]}")
        
        print()
    
    print_separator()
    
    # Summary
    print("📈 SUMMARY:")
    print(f"   Top companies: {', '.join(ranking.top_companies[:3])}")
    if ranking.common_skill_gaps:
        print(f"   Skills to improve: {', '.join(ranking.common_skill_gaps[:5])}")
    
    print_separator()
    print("✅ Demo complete!")
    print("   Run the API server with: uvicorn api.main:app --reload")
    print("   Then visit: http://localhost:8000/docs")
    print_separator()


if __name__ == "__main__":
    main()
