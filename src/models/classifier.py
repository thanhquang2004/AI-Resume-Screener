"""
Classifier - Classify match results into categories.
"""
from typing import Optional
from ..schemas.match_result import MatchCategory


class MatchClassifier:
    """
    Classify match scores into categories.
    
    Categories:
    - POTENTIAL (>75%): Strong candidate, should be considered
    - REVIEW_NEEDED (50-75%): May be suitable, needs review
    - NOT_SUITABLE (<50%): Does not meet requirements
    """
    
    def __init__(self,
                 potential_threshold: float = 0.75,
                 review_threshold: float = 0.50):
        """
        Initialize classifier.
        
        Args:
            potential_threshold: Score threshold for "Potential"
            review_threshold: Score threshold for "Review Needed"
        """
        self.potential_threshold = potential_threshold * 100
        self.review_threshold = review_threshold * 100
    
    def classify(self, score: float) -> MatchCategory:
        """
        Classify a match score.
        
        Args:
            score: Match score (0-100)
            
        Returns:
            MatchCategory
        """
        if score >= self.potential_threshold:
            return MatchCategory.POTENTIAL
        elif score >= self.review_threshold:
            return MatchCategory.REVIEW_NEEDED
        else:
            return MatchCategory.NOT_SUITABLE
    
    def get_label(self, category: MatchCategory) -> str:
        """Get human-readable label for category."""
        labels = {
            MatchCategory.POTENTIAL: "✅ Potential - Strong candidate",
            MatchCategory.REVIEW_NEEDED: "🔍 Review Needed - May be suitable",
            MatchCategory.NOT_SUITABLE: "❌ Not Suitable - Does not meet requirements",
        }
        return labels.get(category, "Unknown")
    
    def get_recommendation(self, category: MatchCategory) -> str:
        """Get action recommendation for category."""
        recommendations = {
            MatchCategory.POTENTIAL: "Schedule an interview",
            MatchCategory.REVIEW_NEEDED: "Review CV in detail before deciding",
            MatchCategory.NOT_SUITABLE: "Consider for other positions",
        }
        return recommendations.get(category, "")


def classify_match(score: float) -> MatchCategory:
    """
    Convenience function to classify a score.
    
    Args:
        score: Match score (0-100)
        
    Returns:
        MatchCategory
    """
    classifier = MatchClassifier()
    return classifier.classify(score)
