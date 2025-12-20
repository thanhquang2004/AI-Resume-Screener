"""
Vectorizer - Convert text to numerical vectors using TF-IDF.
"""
from typing import List, Optional, Tuple, Union
import numpy as np
from pathlib import Path
import pickle

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class TFIDFVectorizer:
    """
    TF-IDF based text vectorizer.
    Converts text documents to numerical vectors for similarity comparison.
    """
    
    def __init__(self,
                 max_features: int = 5000,
                 ngram_range: Tuple[int, int] = (1, 2),
                 min_df: int = 1,
                 max_df: float = 0.95):
        """
        Initialize TF-IDF vectorizer.
        
        Args:
            max_features: Maximum number of features
            ngram_range: N-gram range (1,2) means unigrams and bigrams
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        if not HAS_SKLEARN:
            raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            lowercase=True,
            stop_words='english',
        )
        self.is_fitted = False
    
    def fit(self, documents: List[str]) -> 'TFIDFVectorizer':
        """
        Fit vectorizer on a corpus of documents.
        
        Args:
            documents: List of text documents
            
        Returns:
            Self for chaining
        """
        if not documents:
            raise ValueError("Cannot fit on empty document list")
        
        self.vectorizer.fit(documents)
        self.is_fitted = True
        return self
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform documents to TF-IDF vectors.
        
        Args:
            documents: List of text documents
            
        Returns:
            TF-IDF matrix
        """
        if not self.is_fitted:
            raise RuntimeError("Vectorizer must be fitted first. Call fit() or fit_transform()")
        
        return self.vectorizer.transform(documents).toarray()
    
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit and transform in one step.
        
        Args:
            documents: List of text documents
            
        Returns:
            TF-IDF matrix
        """
        if not documents:
            raise ValueError("Cannot fit on empty document list")
        
        result = self.vectorizer.fit_transform(documents).toarray()
        self.is_fitted = True
        return result
    
    def vectorize(self, text: str) -> np.ndarray:
        """
        Vectorize a single document.
        
        Args:
            text: Text document
            
        Returns:
            TF-IDF vector
        """
        return self.transform([text])[0]
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        # Reshape for sklearn
        v1 = vec1.reshape(1, -1)
        v2 = vec2.reshape(1, -1)
        
        sim = cosine_similarity(v1, v2)[0][0]
        return float(max(0, min(1, sim)))  # Clamp to [0, 1]
    
    def get_feature_names(self) -> List[str]:
        """Get feature names (vocabulary)."""
        if not self.is_fitted:
            return []
        return self.vectorizer.get_feature_names_out().tolist()
    
    def save(self, path: str):
        """Save vectorizer to file."""
        with open(path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def load(self, path: str):
        """Load vectorizer from file."""
        with open(path, 'rb') as f:
            self.vectorizer = pickle.load(f)
            self.is_fitted = True


def create_vectorizer(documents: Optional[List[str]] = None) -> TFIDFVectorizer:
    """
    Create and optionally fit a vectorizer.
    
    Args:
        documents: Optional corpus to fit on
        
    Returns:
        TFIDFVectorizer instance
    """
    vectorizer = TFIDFVectorizer()
    if documents:
        vectorizer.fit(documents)
    return vectorizer
