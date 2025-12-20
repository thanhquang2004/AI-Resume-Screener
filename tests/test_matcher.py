"""
Tests for CV-Job matching functionality.
"""
import pytest


class TestTFIDFVectorizer:
    """Tests for TFIDFVectorizer."""
    
    def test_vectorizer_init(self, vectorizer):
        """Test vectorizer initialization."""
        assert vectorizer is not None
    
    def test_vectorizer_fit(self, vectorizer):
        """Test fitting vectorizer on documents."""
        docs = [
            "python django postgresql",
            "java spring mysql",
            "javascript react nodejs",
        ]
        
        vectorizer.fit(docs)
        assert vectorizer.is_fitted
    
    def test_vectorizer_transform(self, vectorizer):
        """Test transforming text to vector."""
        docs = [
            "python django postgresql",
            "java spring mysql",
        ]
        
        vectorizer.fit(docs)
        vector = vectorizer.transform("python postgresql")
        
        assert vector is not None
        assert len(vector.shape) > 0
    
    def test_vectorizer_similarity(self, vectorizer):
        """Test similarity calculation."""
        docs = [
            "python django postgresql",
            "java spring mysql",
        ]
        
        vectorizer.fit(docs)
        
        # Similar documents should have higher similarity
        sim1 = vectorizer.similarity("python django", "python postgresql")
        sim2 = vectorizer.similarity("python django", "java spring")
        
        assert sim1 > sim2


class TestCVJobMatcher:
    """Tests for CVJobMatcher."""
    
    def test_matcher_init(self, matcher):
        """Test matcher initialization."""
        assert matcher is not None
    
    def test_match_cv_to_job(self, matcher, sample_extracted_cv, sample_job_posting):
        """Test matching a CV to a job posting."""
        result = matcher.match(sample_extracted_cv, sample_job_posting)
        
        assert result is not None
        assert result.cv_id == sample_extracted_cv.cv_id
        assert result.job_id == sample_job_posting.job_id
        assert 0 <= result.score.overall_score <= 1
    
    def test_match_skill_scoring(self, matcher, sample_extracted_cv, sample_job_posting):
        """Test skill score calculation."""
        result = matcher.match(sample_extracted_cv, sample_job_posting)
        
        # CV has python, django, postgresql, aws, docker
        # Job requires python, django, postgresql, aws, docker
        # Should have high skill match
        assert result.score.skill_score > 0.5
    
    def test_match_gap_analysis(self, matcher, sample_extracted_cv, sample_job_posting):
        """Test gap analysis generation."""
        result = matcher.match(sample_extracted_cv, sample_job_posting)
        
        assert result.gap_analysis is not None
        assert isinstance(result.gap_analysis.matched_skills, list)
        assert isinstance(result.gap_analysis.missing_skills, list)
    
    def test_rank_jobs_for_cv(self, matcher, sample_extracted_cv):
        """Test ranking multiple jobs for a single CV."""
        from src.schemas import JobPosting, JobRequirements
        
        jobs = [
            JobPosting(
                job_id="job1",
                title="Python Developer",
                company_name="Company A",
                description="Python web development",
                requirements=JobRequirements(
                    required_skills=["python", "django", "postgresql"],
                    experience_years_min=3,
                ),
                source="test",
            ),
            JobPosting(
                job_id="job2",
                title="Java Developer",
                company_name="Company B",
                description="Java backend development",
                requirements=JobRequirements(
                    required_skills=["java", "spring", "mysql"],
                    experience_years_min=3,
                ),
                source="test",
            ),
            JobPosting(
                job_id="job3",
                title="Full Stack Developer",
                company_name="Company C",
                description="Full stack development",
                requirements=JobRequirements(
                    required_skills=["python", "react", "postgresql", "aws"],
                    experience_years_min=4,
                ),
                source="test",
            ),
        ]
        
        ranking = matcher.match_cv_to_jobs(sample_extracted_cv, jobs)
        
        assert ranking is not None
        assert ranking.cv_id == sample_extracted_cv.cv_id
        assert len(ranking.rankings) == len(jobs)
        
        # Rankings should be sorted by score (highest first)
        scores = [r.score.overall_score for r in ranking.rankings]
        assert scores == sorted(scores, reverse=True)
    
    def test_ranking_categories(self, matcher, sample_extracted_cv):
        """Test that rankings are properly categorized."""
        from src.schemas import JobPosting, JobRequirements, MatchCategory
        
        jobs = [
            JobPosting(
                job_id="good_match",
                title="Python Developer",
                company_name="Good Match Co",
                description="Python Django AWS",
                requirements=JobRequirements(
                    required_skills=["python", "django", "aws"],
                ),
                source="test",
            ),
            JobPosting(
                job_id="poor_match",
                title="Rust Developer",
                company_name="Poor Match Co",
                description="Rust systems programming",
                requirements=JobRequirements(
                    required_skills=["rust", "c++", "systems"],
                ),
                source="test",
            ),
        ]
        
        ranking = matcher.match_cv_to_jobs(sample_extracted_cv, jobs)
        
        # Good match should be ranked higher
        assert ranking.rankings[0].job_id == "good_match"
        
        # Categories should be assigned
        for r in ranking.rankings:
            assert r.score.category in [
                MatchCategory.POTENTIAL,
                MatchCategory.REVIEW_NEEDED,
                MatchCategory.NOT_SUITABLE,
            ]


class TestMatchClassifier:
    """Tests for MatchClassifier."""
    
    def test_classifier_init(self, classifier):
        """Test classifier initialization."""
        assert classifier is not None
        assert classifier.potential_threshold > classifier.review_threshold
    
    def test_classify_potential(self, classifier):
        """Test classification of high scores."""
        from src.schemas import MatchCategory
        
        category = classifier.classify(0.85)
        assert category == MatchCategory.POTENTIAL
    
    def test_classify_review_needed(self, classifier):
        """Test classification of medium scores."""
        from src.schemas import MatchCategory
        
        category = classifier.classify(0.60)
        assert category == MatchCategory.REVIEW_NEEDED
    
    def test_classify_not_suitable(self, classifier):
        """Test classification of low scores."""
        from src.schemas import MatchCategory
        
        category = classifier.classify(0.30)
        assert category == MatchCategory.NOT_SUITABLE
    
    def test_classify_boundary_values(self, classifier):
        """Test classification at threshold boundaries."""
        from src.schemas import MatchCategory
        
        # At potential threshold
        assert classifier.classify(0.75) == MatchCategory.POTENTIAL
        
        # Just below potential threshold
        assert classifier.classify(0.74) == MatchCategory.REVIEW_NEEDED
        
        # At review threshold
        assert classifier.classify(0.50) == MatchCategory.REVIEW_NEEDED
        
        # Just below review threshold
        assert classifier.classify(0.49) == MatchCategory.NOT_SUITABLE
    
    def test_custom_thresholds(self):
        """Test classifier with custom thresholds."""
        from src.models import MatchClassifier
        from src.schemas import MatchCategory
        
        classifier = MatchClassifier(
            potential_threshold=0.8,
            review_threshold=0.6,
        )
        
        assert classifier.classify(0.85) == MatchCategory.POTENTIAL
        assert classifier.classify(0.70) == MatchCategory.REVIEW_NEEDED
        assert classifier.classify(0.50) == MatchCategory.NOT_SUITABLE
