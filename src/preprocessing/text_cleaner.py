"""
Text Cleaner - Preprocessing and normalization of text.
"""
from typing import List, Optional, Set
import re
import string


class TextCleaner:
    """
    Clean and normalize text for NLP processing.
    Handles both English and Vietnamese text.
    """
    
    # Stopwords (English + Vietnamese common words)
    STOPWORDS_EN: Set[str] = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'we', 'you', 'he', 'she', 'it', 'they', 'i', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
        'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom',
        'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only',
        'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
    }
    
    STOPWORDS_VI: Set[str] = {
        'là', 'và', 'có', 'được', 'để', 'với', 'trong', 'cho', 'của',
        'các', 'này', 'đó', 'như', 'về', 'khi', 'từ', 'một', 'những',
        'trên', 'đã', 'sẽ', 'còn', 'mà', 'hoặc', 'hay', 'nếu', 'thì',
        'tại', 'bởi', 'theo', 'qua', 'sau', 'trước', 'giữa',
        'tôi', 'bạn', 'chúng tôi', 'họ', 'anh', 'chị', 'em',
        'rất', 'nhiều', 'ít', 'hơn', 'nhất', 'nào', 'gì', 'đâu',
    }
    
    def __init__(self, 
                 remove_stopwords: bool = True,
                 lowercase: bool = True,
                 remove_punctuation: bool = False,
                 remove_numbers: bool = False):
        """
        Initialize text cleaner.
        
        Args:
            remove_stopwords: Remove common stopwords
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation marks
            remove_numbers: Remove numeric characters
        """
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        
        self.stopwords = self.STOPWORDS_EN | self.STOPWORDS_VI
    
    def clean(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = self._remove_html(text)
        
        # Remove URLs
        text = self._remove_urls(text)
        
        # Remove email addresses (for privacy)
        text = self._remove_emails(text)
        
        # Remove phone numbers (for privacy)
        text = self._remove_phones(text)
        
        # Normalize whitespace
        text = self._normalize_whitespace(text)
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove punctuation (but keep some for tech terms like C++, C#)
        if self.remove_punctuation:
            text = self._remove_punctuation(text)
        
        # Remove numbers
        if self.remove_numbers:
            text = self._remove_numbers(text)
        
        # Remove stopwords
        if self.remove_stopwords:
            text = self._remove_stopwords(text)
        
        # Final whitespace cleanup
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags."""
        return re.sub(r'<[^>]+>', ' ', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs."""
        return re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses."""
        return re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', ' ', text)
    
    def _remove_phones(self, text: str) -> str:
        """Remove phone numbers."""
        return re.sub(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', ' ', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _remove_punctuation(self, text: str) -> str:
        """Remove punctuation, keeping tech-relevant chars."""
        # Keep: + # . (for C++, C#, .NET)
        chars_to_keep = {'+', '#', '.'}
        result = []
        for char in text:
            if char in chars_to_keep or char not in string.punctuation:
                result.append(char)
            else:
                result.append(' ')
        return ''.join(result)
    
    def _remove_numbers(self, text: str) -> str:
        """Remove standalone numbers but keep version numbers."""
        # Keep numbers that are part of words (Python3, Vue2)
        return re.sub(r'\b\d+\b', ' ', text)
    
    def _remove_stopwords(self, text: str) -> str:
        """Remove stopwords."""
        words = text.split()
        filtered = [w for w in words if w.lower() not in self.stopwords]
        return ' '.join(filtered)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Simple whitespace tokenization
        tokens = text.split()
        return [t.strip() for t in tokens if t.strip()]


def clean_text(text: str, 
               remove_stopwords: bool = True,
               lowercase: bool = True) -> str:
    """
    Convenience function to clean text.
    
    Args:
        text: Raw text
        remove_stopwords: Remove stopwords
        lowercase: Convert to lowercase
        
    Returns:
        Cleaned text
    """
    cleaner = TextCleaner(
        remove_stopwords=remove_stopwords,
        lowercase=lowercase,
    )
    return cleaner.clean(text)
