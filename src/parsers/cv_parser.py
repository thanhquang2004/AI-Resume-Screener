"""
CV Parser - Extract structured information from CV text.
"""
from typing import List, Optional, Tuple
from pathlib import Path
import re
import uuid
from datetime import datetime

from ..schemas.cv import CVData, ExtractedCV, Education, Experience, EducationLevel
from .pdf_parser import PDFParser
from .docx_parser import DocxParser


class CVParser:
    """
    Parse CV files and extract structured information.
    Combines file parsing with information extraction.
    """
    
    # Common section headers
    SECTION_PATTERNS = {
        'education': r'(?i)(education|học vấn|trình độ|bằng cấp)',
        'experience': r'(?i)(experience|work history|kinh nghiệm|công việc)',
        'skills': r'(?i)(skills|technical skills|kỹ năng|chuyên môn)',
        'projects': r'(?i)(projects|dự án)',
        'summary': r'(?i)(summary|objective|profile|giới thiệu|mục tiêu)',
        'certifications': r'(?i)(certifications?|certificates?|chứng chỉ)',
    }
    
    # Common IT skills pattern
    SKILL_PATTERNS = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|go|rust|swift|kotlin)\b',
        r'\b(react|vue|angular|node\.?js|django|flask|spring|express|laravel|rails)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|dynamodb|oracle)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible)\b',
        r'\b(git|github|gitlab|jira|linux|bash|nginx|apache)\b',
        r'\b(html|css|sass|bootstrap|tailwind|webpack|babel)\b',
        r'\b(tensorflow|pytorch|keras|scikit-learn|pandas|numpy)\b',
        r'\b(restful?|graphql|microservices|api|ci/cd|agile|scrum)\b',
    ]
    
    # Experience years pattern
    EXPERIENCE_PATTERN = r'(\d+)\+?\s*(?:years?|năm|yrs?)'
    
    # Education level patterns
    EDUCATION_LEVELS = {
        EducationLevel.PHD: r'(?i)(ph\.?d|tiến sĩ|doctor)',
        EducationLevel.MASTER: r'(?i)(master|thạc sĩ|m\.?s\.?|m\.?sc)',
        EducationLevel.BACHELOR: r'(?i)(bachelor|cử nhân|b\.?s\.?|b\.?sc|đại học)',
    }
    
    def __init__(self):
        """Initialize CV parser."""
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
    
    def parse_file(self, file_path: str) -> CVData:
        """
        Parse a CV file (PDF or DOCX).
        
        Args:
            file_path: Path to CV file
            
        Returns:
            CVData with raw text
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            raw_text = self.pdf_parser.parse(file_path)
            file_type = 'pdf'
        elif suffix in ['.docx', '.doc']:
            raw_text = self.docx_parser.parse(file_path)
            file_type = 'docx'
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        return CVData(
            cv_id=str(uuid.uuid4())[:8],
            filename=path.name,
            file_type=file_type,
            raw_text=raw_text,
        )
    
    def parse_bytes(self, file_bytes: bytes, filename: str) -> CVData:
        """
        Parse CV from bytes.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            CVData with raw text
        """
        suffix = Path(filename).suffix.lower()
        
        if suffix == '.pdf':
            raw_text = self.pdf_parser.parse_bytes(file_bytes)
            file_type = 'pdf'
        elif suffix in ['.docx', '.doc']:
            raw_text = self.docx_parser.parse_bytes(file_bytes)
            file_type = 'docx'
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        return CVData(
            cv_id=str(uuid.uuid4())[:8],
            filename=filename,
            file_type=file_type,
            raw_text=raw_text,
        )
    
    def extract_info(self, cv_data: CVData) -> ExtractedCV:
        """
        Extract structured information from CV text.
        
        Args:
            cv_data: Parsed CV with raw text
            
        Returns:
            ExtractedCV with structured data
        """
        text = cv_data.raw_text
        
        # Extract skills
        technical_skills = self._extract_skills(text)
        
        # Extract experience
        experiences, total_years = self._extract_experience(text)
        
        # Extract education
        education, highest_level = self._extract_education(text)
        
        # Extract contact info (optional, can be anonymized)
        name = self._extract_name(text)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        
        return ExtractedCV(
            cv_id=cv_data.cv_id,
            name=name,
            email=email,
            phone=phone,
            technical_skills=technical_skills,
            all_skills=technical_skills,
            experiences=experiences,
            total_experience_years=total_years,
            education=education,
            highest_education=highest_level,
            raw_text=text,
            extracted_at=datetime.now(),
        )
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        skills = set()
        text_lower = text.lower()
        
        for pattern in self.SKILL_PATTERNS:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)
        
        # Normalize
        normalized = []
        for skill in skills:
            skill = skill.strip()
            if skill:
                normalized.append(skill)
        
        return list(set(normalized))
    
    def _extract_experience(self, text: str) -> Tuple[List[Experience], float]:
        """Extract work experience."""
        experiences = []
        total_years = 0.0
        
        # Find experience years mentions
        matches = re.findall(self.EXPERIENCE_PATTERN, text, re.IGNORECASE)
        if matches:
            years = [int(m) for m in matches]
            total_years = max(years) if years else 0.0
        
        # TODO: More sophisticated experience extraction with NER
        # For now, just return the years found
        
        return experiences, total_years
    
    def _extract_education(self, text: str) -> Tuple[List[Education], EducationLevel]:
        """Extract education information."""
        education = []
        highest_level = EducationLevel.BACHELOR
        
        # Check for education levels
        for level, pattern in self.EDUCATION_LEVELS.items():
            if re.search(pattern, text):
                highest_level = level
                break
        
        return education, highest_level
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name (first line usually)."""
        lines = text.strip().split('\n')
        if lines:
            # First non-empty line is often the name
            first_line = lines[0].strip()
            # Filter out if it looks like a header
            if len(first_line) < 50 and not any(kw in first_line.lower() for kw in ['resume', 'cv', 'curriculum']):
                return first_line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address."""
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number."""
        pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        match = re.search(pattern, text)
        return match.group(0) if match else None


def parse_cv(file_path: str) -> ExtractedCV:
    """
    Convenience function to parse a CV file.
    
    Args:
        file_path: Path to CV file
        
    Returns:
        ExtractedCV with structured data
    """
    parser = CVParser()
    cv_data = parser.parse_file(file_path)
    return parser.extract_info(cv_data)
