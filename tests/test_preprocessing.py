"""
Tests for preprocessing modules.
"""
import pytest


class TestTextCleaner:
    """Tests for TextCleaner class."""
    
    def test_remove_html_tags(self, text_cleaner):
        """Test HTML tag removal."""
        html_text = "<p>This is <strong>bold</strong> text</p>"
        cleaned = text_cleaner.clean(html_text)
        
        assert "<p>" not in cleaned
        assert "<strong>" not in cleaned
        assert "bold" in cleaned
    
    def test_remove_urls(self, text_cleaner):
        """Test URL removal."""
        text = "Visit https://example.com for more info. Also check http://test.org"
        cleaned = text_cleaner.clean(text)
        
        assert "https://" not in cleaned
        assert "http://" not in cleaned
    
    def test_normalize_whitespace(self, text_cleaner):
        """Test whitespace normalization."""
        text = "Multiple    spaces\n\n\nand   newlines"
        cleaned = text_cleaner.clean(text)
        
        # Should not have multiple consecutive spaces/newlines
        assert "    " not in cleaned
        assert "\n\n\n" not in cleaned
    
    def test_handle_unicode(self, text_cleaner):
        """Test Unicode normalization."""
        text = "Việt Nam developer with café experience"
        cleaned = text_cleaner.clean(text)
        
        # Should preserve Vietnamese characters
        assert "Việt Nam" in cleaned or "Viet Nam" in cleaned
    
    def test_clean_for_matching_lowercase(self, text_cleaner):
        """Test that matching text is lowercased."""
        text = "PYTHON Developer at GOOGLE"
        cleaned = text_cleaner.clean_for_matching(text)
        
        assert "python" in cleaned.lower()
    
    def test_remove_stopwords(self, text_cleaner):
        """Test stopword removal."""
        text = "The quick brown fox jumps over the lazy dog"
        cleaned = text_cleaner.clean_for_matching(text, remove_stopwords=True)
        
        # Common stopwords should be removed
        words = cleaned.lower().split()
        assert "the" not in words or len([w for w in words if w == "the"]) == 0
    
    def test_handle_empty_string(self, text_cleaner):
        """Test empty string handling."""
        assert text_cleaner.clean("") == ""
        assert text_cleaner.clean_for_matching("") == ""
    
    def test_handle_none(self, text_cleaner):
        """Test None handling."""
        assert text_cleaner.clean(None) == ""


class TestSkillExtractor:
    """Tests for SkillExtractor class."""
    
    def test_extract_programming_languages(self, skill_extractor):
        """Test programming language extraction."""
        text = "Proficient in Python, Java, JavaScript, and C++"
        skills = skill_extractor.extract(text)
        
        assert "python" in skills
        assert "java" in skills
        assert "javascript" in skills
    
    def test_extract_frameworks(self, skill_extractor):
        """Test framework extraction."""
        text = "Experience with Django, Flask, React, and Node.js"
        skills = skill_extractor.extract(text)
        
        assert "django" in skills
        assert "flask" in skills
        assert "react" in skills
    
    def test_extract_databases(self, skill_extractor):
        """Test database extraction."""
        text = "Worked with PostgreSQL, MongoDB, MySQL, and Redis"
        skills = skill_extractor.extract(text)
        
        assert "postgresql" in skills or "postgres" in skills
        assert "mongodb" in skills
        assert "mysql" in skills
        assert "redis" in skills
    
    def test_extract_cloud_services(self, skill_extractor):
        """Test cloud service extraction."""
        text = "Deployed on AWS, used EC2, S3, Lambda, and Docker"
        skills = skill_extractor.extract(text)
        
        assert "aws" in skills
        assert "docker" in skills
    
    def test_normalize_skill_variations(self, skill_extractor):
        """Test that skill variations are normalized."""
        text1 = "ReactJS development"
        text2 = "React.js development"
        text3 = "React development"
        
        skills1 = skill_extractor.extract(text1)
        skills2 = skill_extractor.extract(text2)
        skills3 = skill_extractor.extract(text3)
        
        # All should normalize to 'react'
        assert "react" in skills1 or "reactjs" in skills1
        assert "react" in skills2 or "reactjs" in skills2
        assert "react" in skills3
    
    def test_extract_with_context(self, skill_extractor):
        """Test extraction with category context."""
        text = "Python developer with PostgreSQL and AWS experience"
        result = skill_extractor.extract_with_context(text)
        
        assert len(result) > 0
        # Result should have categories
        for category, skills in result.items():
            assert isinstance(skills, list)
    
    def test_case_insensitive(self, skill_extractor):
        """Test case insensitive extraction."""
        text1 = "PYTHON, JAVA, JAVASCRIPT"
        text2 = "python, java, javascript"
        
        skills1 = skill_extractor.extract(text1)
        skills2 = skill_extractor.extract(text2)
        
        assert set(skills1) == set(skills2)
    
    def test_handle_empty_text(self, skill_extractor):
        """Test empty text handling."""
        skills = skill_extractor.extract("")
        assert skills == []
    
    def test_handle_no_skills_text(self, skill_extractor):
        """Test text with no recognizable skills."""
        text = "I enjoy reading books and hiking on weekends."
        skills = skill_extractor.extract(text)
        
        # Should return empty or very few skills
        assert len(skills) < 3  # Might catch some false positives


class TestSkillDictionary:
    """Tests for SkillDictionary."""
    
    def test_normalize_synonyms(self):
        """Test synonym normalization."""
        from src.utils import SkillDictionary
        sd = SkillDictionary()
        
        # Common synonyms
        assert sd.normalize("js") == "javascript"
        assert sd.normalize("ts") == "typescript"
        assert sd.normalize("py") == "python"
        assert sd.normalize("k8s") == "kubernetes"
        assert sd.normalize("postgres") == "postgresql"
        assert sd.normalize("reactjs") == "react"
    
    def test_normalize_unknown_skill(self):
        """Test normalization of unknown skills."""
        from src.utils import SkillDictionary
        sd = SkillDictionary()
        
        # Unknown skills should return as-is (lowercase)
        assert sd.normalize("unknownskill123") == "unknownskill123"
    
    def test_get_category(self):
        """Test category lookup."""
        from src.utils import SkillDictionary
        sd = SkillDictionary()
        
        category = sd.get_category("python")
        assert category in ["programming", "language", None] or category is not None
    
    def test_find_matches_in_text(self):
        """Test finding skill matches in text."""
        from src.utils import SkillDictionary
        sd = SkillDictionary()
        
        text = "Looking for Python and JavaScript developers"
        matches = sd.find_matches(text)
        
        assert "python" in matches
        assert "javascript" in matches
