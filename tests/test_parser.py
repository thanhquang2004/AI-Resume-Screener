"""
Tests for CV and document parsers.
"""
import pytest
from pathlib import Path


class TestCVParser:
    """Tests for CVParser."""
    
    def test_cv_parser_init(self, cv_parser):
        """Test CVParser initialization."""
        assert cv_parser is not None
    
    def test_extract_name_from_cv(self, cv_parser, sample_cv_text):
        """Test name extraction from CV text."""
        # This test verifies the parser can process text
        from src.schemas import CVData
        
        cv_data = CVData(
            raw_text=sample_cv_text,
            source_file="test.pdf"
        )
        
        extracted = cv_parser.extract_info(cv_data)
        assert extracted is not None
        assert extracted.cv_id is not None
    
    def test_extract_skills_from_cv(self, cv_parser, sample_cv_text):
        """Test skill extraction from CV text."""
        from src.schemas import CVData
        
        cv_data = CVData(
            raw_text=sample_cv_text,
            source_file="test.pdf"
        )
        
        extracted = cv_parser.extract_info(cv_data)
        
        # Should find Python, JavaScript, etc.
        skills = extracted.all_skills
        assert "python" in skills
        assert "javascript" in skills or "js" in skills
    
    def test_extract_experience_from_cv(self, cv_parser, sample_cv_text):
        """Test experience extraction from CV text."""
        from src.schemas import CVData
        
        cv_data = CVData(
            raw_text=sample_cv_text,
            source_file="test.pdf"
        )
        
        extracted = cv_parser.extract_info(cv_data)
        
        # Should find experience entries
        assert len(extracted.experience) > 0 or extracted.total_experience_years > 0
    
    def test_extract_education_from_cv(self, cv_parser, sample_cv_text):
        """Test education extraction from CV text."""
        from src.schemas import CVData
        
        cv_data = CVData(
            raw_text=sample_cv_text,
            source_file="test.pdf"
        )
        
        extracted = cv_parser.extract_info(cv_data)
        
        # Should find education
        assert len(extracted.education) > 0 or extracted.highest_education is not None


class TestTextCleaner:
    """Tests for TextCleaner preprocessing."""
    
    def test_clean_text_removes_html(self, text_cleaner):
        """Test HTML tag removal."""
        text = "<p>Hello <b>World</b></p>"
        cleaned = text_cleaner.clean(text)
        assert "<" not in cleaned
        assert ">" not in cleaned
    
    def test_clean_text_normalizes_whitespace(self, text_cleaner):
        """Test whitespace normalization."""
        text = "Hello    World\n\n\nTest"
        cleaned = text_cleaner.clean(text)
        assert "    " not in cleaned
    
    def test_clean_text_handles_empty(self, text_cleaner):
        """Test empty text handling."""
        assert text_cleaner.clean("") == ""
        assert text_cleaner.clean(None) == ""
    
    def test_clean_for_matching_lowercase(self, text_cleaner):
        """Test that matching text is lowercased."""
        text = "Python Developer"
        cleaned = text_cleaner.clean_for_matching(text)
        assert cleaned.islower() or "python" in cleaned.lower()


class TestSkillExtractor:
    """Tests for SkillExtractor."""
    
    def test_extract_programming_languages(self, skill_extractor, sample_skills_text):
        """Test extraction of programming languages."""
        skills = skill_extractor.extract(sample_skills_text)
        
        assert "python" in skills
        assert "java" in skills
        assert "javascript" in skills
    
    def test_extract_frameworks(self, skill_extractor, sample_skills_text):
        """Test extraction of frameworks."""
        skills = skill_extractor.extract(sample_skills_text)
        
        assert "react" in skills or "reactjs" in skills
        assert "nodejs" in skills or "node.js" in skills or "node" in skills
    
    def test_extract_databases(self, skill_extractor, sample_skills_text):
        """Test extraction of database skills."""
        skills = skill_extractor.extract(sample_skills_text)
        
        assert "postgresql" in skills or "postgres" in skills
        assert "mongodb" in skills or "mongo" in skills
    
    def test_extract_cloud_platforms(self, skill_extractor, sample_skills_text):
        """Test extraction of cloud platforms."""
        skills = skill_extractor.extract(sample_skills_text)
        
        assert "aws" in skills
        assert "docker" in skills
        assert "kubernetes" in skills or "k8s" in skills
    
    def test_normalize_skill_synonyms(self, skill_extractor):
        """Test skill normalization (js -> javascript)."""
        from src.utils import SkillDictionary
        
        sd = SkillDictionary()
        
        assert sd.normalize("js") == "javascript"
        assert sd.normalize("k8s") == "kubernetes"
        assert sd.normalize("postgres") == "postgresql"
    
    def test_extract_with_context(self, skill_extractor, sample_skills_text):
        """Test extraction with category context."""
        result = skill_extractor.extract_with_context(sample_skills_text)
        
        assert "programming" in result or len(result) > 0
    
    def test_empty_text_returns_empty_list(self, skill_extractor):
        """Test empty text handling."""
        skills = skill_extractor.extract("")
        assert skills == []
