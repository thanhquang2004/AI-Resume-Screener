"""
Matcher - Match CV to Job postings and calculate similarity scores.
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime

from ..schemas.cv import ExtractedCV
from ..schemas.job import JobPosting
from ..schemas.match_result import (
    MatchResult, MatchScore, GapAnalysis, CompanyRanking, MatchCategory
)
from ..utils.skill_dictionary import SkillDictionary
from ..preprocessing.skill_extractor import SkillExtractor
from .vectorizer import TFIDFVectorizer


class CVJobMatcher:
    """
    Match CVs to Job postings using multiple signals:
    - Skill matching (keyword overlap)
    - Text similarity (TF-IDF + Cosine)
    - Experience matching
    """
    
    # Weights for different matching components
    DEFAULT_WEIGHTS = {
        'skill_match': 0.50,      # 50% weight on skill matching
        'text_similarity': 0.35,  # 35% weight on semantic similarity
        'experience_match': 0.15, # 15% weight on experience
    }
    
    def __init__(self, 
                 weights: Optional[Dict[str, float]] = None,
                 potential_threshold: float = 0.75,
                 review_threshold: float = 0.50):
        """
        Initialize matcher.
        
        Args:
            weights: Custom weights for matching components
            potential_threshold: Score threshold for "Potential" (>75%)
            review_threshold: Score threshold for "Review Needed" (>50%)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.potential_threshold = potential_threshold
        self.review_threshold = review_threshold
        
        self.skill_dict = SkillDictionary()
        self.skill_extractor = SkillExtractor(self.skill_dict)
        self.vectorizer: Optional[TFIDFVectorizer] = None
    
    def fit_vectorizer(self, documents: List[str]):
        """
        Fit the TF-IDF vectorizer on a corpus.
        
        Args:
            documents: List of text documents (JDs + CVs)
        """
        self.vectorizer = TFIDFVectorizer()
        self.vectorizer.fit(documents)
    
    def match(self, cv: ExtractedCV, job: JobPosting) -> MatchResult:
        """
        Match a CV against a job posting.
        
        Args:
            cv: Extracted CV data
            job: Job posting
            
        Returns:
            MatchResult with scores and gap analysis
        """
        # Extract skills from JD if not already done
        jd_skills = job.requirements.required_skills
        if not jd_skills:
            jd_text = job.get_full_text()
            jd_skills = self.skill_extractor.extract(jd_text)
        
        # Get CV skills
        cv_skills = cv.get_all_skills()
        if not cv_skills:
            cv_skills = self.skill_extractor.extract(cv.get_searchable_text())
        
        # Calculate skill match
        skill_score, matched, missing, extra = self._calculate_skill_match(
            cv_skills, jd_skills
        )
        
        # Calculate text similarity
        text_similarity = self._calculate_text_similarity(cv, job)
        
        # Calculate experience match
        experience_score = self._calculate_experience_match(
            cv.total_experience_years,
            job.requirements.experience_years_min,
            job.requirements.experience_years_max,
        )
        
        # Calculate overall score
        overall_score = (
            self.weights['skill_match'] * skill_score +
            self.weights['text_similarity'] * text_similarity * 100 +
            self.weights['experience_match'] * experience_score
        )
        
        # Classify
        category = self._classify(overall_score)
        
        # Build gap analysis
        gap_analysis = GapAnalysis(
            matched_skills=matched,
            missing_skills=missing,
            extra_skills=extra,
            skill_match_ratio=len(matched) / len(jd_skills) if jd_skills else 0,
            required_experience_years=job.requirements.experience_years_min,
            candidate_experience_years=cv.total_experience_years,
            experience_gap=(job.requirements.experience_years_min or 0) - cv.total_experience_years,
            recommendations=self._generate_recommendations(missing, experience_score),
        )
        
        return MatchResult(
            cv_id=cv.cv_id,
            job_id=job.job_id,
            job_title=job.title,
            company_name=job.company_name,
            score=MatchScore(
                overall_score=round(overall_score, 2),
                category=category,
                skill_score=round(skill_score, 2),
                experience_score=round(experience_score, 2),
                text_similarity=round(text_similarity, 4),
            ),
            gap_analysis=gap_analysis,
            matched_at=datetime.now(),
        )
    
    def match_cv_to_jobs(self, 
                         cv: ExtractedCV, 
                         jobs: List[JobPosting],
                         top_n: Optional[int] = None) -> CompanyRanking:
        """
        Match a CV against multiple job postings and rank them.
        
        Args:
            cv: Extracted CV data
            jobs: List of job postings
            top_n: Return only top N results
            
        Returns:
            CompanyRanking with sorted results
        """
        # Fit vectorizer if needed
        if self.vectorizer is None or not self.vectorizer.is_fitted:
            all_texts = [job.get_full_text() for job in jobs]
            all_texts.append(cv.get_searchable_text())
            self.fit_vectorizer(all_texts)
        
        # Match against all jobs
        results: List[MatchResult] = []
        for job in jobs:
            result = self.match(cv, job)
            results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda x: x.score.overall_score, reverse=True)
        
        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        # Apply top_n filter
        if top_n:
            results = results[:top_n]
        
        # Count by category
        potential_count = sum(1 for r in results if r.score.category == MatchCategory.POTENTIAL)
        review_count = sum(1 for r in results if r.score.category == MatchCategory.REVIEW_NEEDED)
        not_suitable_count = sum(1 for r in results if r.score.category == MatchCategory.NOT_SUITABLE)
        
        # Find common skill gaps (from top matches)
        top_matches = [r for r in results if r.score.overall_score >= 50][:5]
        common_gaps = self._find_common_gaps(top_matches)
        
        return CompanyRanking(
            cv_id=cv.cv_id,
            candidate_name=cv.name,
            candidate_skills=cv.get_all_skills(),
            rankings=results,
            total_jobs_analyzed=len(jobs),
            potential_count=potential_count,
            review_needed_count=review_count,
            not_suitable_count=not_suitable_count,
            top_companies=[r.company_name for r in results[:5]],
            common_skill_gaps=common_gaps,
            generated_at=datetime.now(),
        )
    
    def _calculate_skill_match(self, 
                                cv_skills: List[str],
                                jd_skills: List[str]) -> Tuple[float, List[str], List[str], List[str]]:
        """Calculate skill matching score."""
        if not jd_skills:
            return 100.0, [], [], list(cv_skills)
        
        # Normalize all skills
        cv_normalized = {self.skill_dict.normalize(s) for s in cv_skills if s}
        jd_normalized = {self.skill_dict.normalize(s) for s in jd_skills if s}
        
        # Find matches
        matched = list(cv_normalized & jd_normalized)
        missing = list(jd_normalized - cv_normalized)
        extra = list(cv_normalized - jd_normalized)
        
        # Calculate score (percentage of JD skills matched)
        match_ratio = len(matched) / len(jd_normalized) if jd_normalized else 0
        score = match_ratio * 100
        
        return score, matched, missing, extra
    
    def _calculate_text_similarity(self, cv: ExtractedCV, job: JobPosting) -> float:
        """Calculate text similarity using TF-IDF + Cosine."""
        if self.vectorizer is None or not self.vectorizer.is_fitted:
            return 0.0
        
        cv_text = cv.get_searchable_text()
        jd_text = job.get_full_text()
        
        if not cv_text or not jd_text:
            return 0.0
        
        try:
            cv_vector = self.vectorizer.vectorize(cv_text)
            jd_vector = self.vectorizer.vectorize(jd_text)
            similarity = self.vectorizer.similarity(cv_vector, jd_vector)
            return similarity
        except Exception:
            return 0.0
    
    def _calculate_experience_match(self,
                                     candidate_years: float,
                                     required_min: Optional[int],
                                     required_max: Optional[int]) -> float:
        """Calculate experience matching score."""
        if required_min is None:
            return 100.0  # No requirement
        
        if candidate_years >= required_min:
            if required_max is None or candidate_years <= required_max:
                return 100.0  # Perfect match
            else:
                # Overqualified (slight penalty)
                over = candidate_years - required_max
                return max(70.0, 100.0 - over * 5)
        else:
            # Underqualified
            gap = required_min - candidate_years
            if gap <= 1:
                return 70.0  # Close enough
            elif gap <= 2:
                return 50.0
            else:
                return max(20.0, 50.0 - gap * 10)
    
    def _classify(self, score: float) -> MatchCategory:
        """Classify match based on score."""
        if score >= self.potential_threshold * 100:
            return MatchCategory.POTENTIAL
        elif score >= self.review_threshold * 100:
            return MatchCategory.REVIEW_NEEDED
        else:
            return MatchCategory.NOT_SUITABLE
    
    def _generate_recommendations(self, 
                                   missing_skills: List[str],
                                   experience_score: float) -> List[str]:
        """Generate recommendations for the candidate."""
        recommendations = []
        
        if missing_skills:
            if len(missing_skills) <= 3:
                recommendations.append(
                    f"Consider learning: {', '.join(missing_skills)}"
                )
            else:
                recommendations.append(
                    f"Missing {len(missing_skills)} required skills. "
                    f"Priority: {', '.join(missing_skills[:3])}"
                )
        
        if experience_score < 70:
            recommendations.append(
                "More experience may be needed for this role"
            )
        
        if not recommendations:
            recommendations.append("Strong match! Consider applying.")
        
        return recommendations
    
    def _find_common_gaps(self, results: List[MatchResult]) -> List[str]:
        """Find skills commonly missing across top matches."""
        if not results:
            return []
        
        skill_counts: Dict[str, int] = {}
        for result in results:
            for skill in result.gap_analysis.missing_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, count in sorted_skills[:5]]


def match_cv_to_job(cv: ExtractedCV, job: JobPosting) -> MatchResult:
    """
    Convenience function to match a CV to a job.
    
    Args:
        cv: Extracted CV data
        job: Job posting
        
    Returns:
        MatchResult
    """
    matcher = CVJobMatcher()
    return matcher.match(cv, job)
