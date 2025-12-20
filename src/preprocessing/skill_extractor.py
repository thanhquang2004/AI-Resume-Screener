"""
Skill Extractor - Extract and normalize technical skills from text.
"""
from typing import List, Set, Dict, Optional
import re

from ..utils.skill_dictionary import SkillDictionary


class SkillExtractor:
    """
    Extract technical skills from text using pattern matching
    and a skill dictionary.
    """
    
    # Comprehensive skill patterns
    SKILL_PATTERNS: List[str] = [
        # Programming Languages
        r'\b(python|java|javascript|typescript|c\+\+|c#|csharp|ruby|php|go|golang|rust|swift|kotlin|scala|r|matlab|perl)\b',
        
        # Web Frontend
        r'\b(react|reactjs|react\.js|vue|vuejs|vue\.js|angular|angularjs|svelte|nextjs|next\.js|nuxtjs|nuxt\.js)\b',
        r'\b(html5?|css3?|sass|scss|less|tailwind|bootstrap|jquery|webpack|vite|babel)\b',
        r'\b(redux|mobx|vuex|pinia|graphql|apollo)\b',
        
        # Web Backend
        r'\b(nodejs|node\.js|express|expressjs|django|flask|fastapi|spring|springboot|spring boot)\b',
        r'\b(rails|ruby on rails|laravel|symfony|asp\.net|aspnet|\.net|dotnet|nestjs)\b',
        
        # Mobile
        r'\b(android|ios|react native|flutter|xamarin|ionic|swift|swiftui|kotlin)\b',
        
        # Databases
        r'\b(sql|mysql|postgresql|postgres|mongodb|mongo|redis|elasticsearch|cassandra)\b',
        r'\b(dynamodb|oracle|mssql|sql server|sqlite|mariadb|neo4j|firebase)\b',
        
        # Cloud & DevOps
        r'\b(aws|amazon web services|azure|gcp|google cloud|heroku|digitalocean|vercel|netlify)\b',
        r'\b(docker|kubernetes|k8s|jenkins|gitlab|github actions|circleci|travis)\b',
        r'\b(terraform|ansible|puppet|chef|vagrant|helm|argocd)\b',
        r'\b(ci/cd|cicd|devops|sre|linux|unix|bash|shell|powershell)\b',
        r'\b(nginx|apache|prometheus|grafana|elk|datadog|splunk)\b',
        
        # Data & ML
        r'\b(machine learning|deep learning|ml|dl|ai|artificial intelligence)\b',
        r'\b(tensorflow|pytorch|keras|scikit-learn|sklearn|pandas|numpy|scipy)\b',
        r'\b(spark|hadoop|airflow|kafka|flink|hive|presto|snowflake|databricks)\b',
        r'\b(nlp|computer vision|opencv|huggingface|transformers|bert|gpt)\b',
        
        # Tools & Others
        r'\b(git|github|gitlab|bitbucket|svn|mercurial)\b',
        r'\b(jira|confluence|trello|asana|slack|notion)\b',
        r'\b(figma|sketch|adobe xd|photoshop|illustrator)\b',
        r'\b(rest|restful|api|microservices|grpc|websocket|soap)\b',
        r'\b(agile|scrum|kanban|waterfall|lean)\b',
        r'\b(tdd|bdd|unit testing|integration testing|e2e|selenium|cypress|jest|pytest)\b',
    ]
    
    def __init__(self, skill_dict: Optional[SkillDictionary] = None):
        """
        Initialize skill extractor.
        
        Args:
            skill_dict: Skill dictionary for normalization
        """
        self.skill_dict = skill_dict or SkillDictionary()
        
        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SKILL_PATTERNS
        ]
    
    def extract(self, text: str) -> List[str]:
        """
        Extract skills from text.
        
        Args:
            text: Input text (CV or JD)
            
        Returns:
            List of normalized skills
        """
        if not text:
            return []
        
        skills: Set[str] = set()
        
        # Apply all patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                # Normalize skill
                normalized = self.skill_dict.normalize(match)
                if normalized:
                    skills.add(normalized)
        
        return sorted(list(skills))
    
    def extract_with_context(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills grouped by category.
        
        Args:
            text: Input text
            
        Returns:
            Dict mapping category to list of skills
        """
        skills = self.extract(text)
        
        categorized: Dict[str, List[str]] = {}
        uncategorized: List[str] = []
        
        for skill in skills:
            category = self.skill_dict.get_category(skill)
            if category:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(skill)
            else:
                uncategorized.append(skill)
        
        if uncategorized:
            categorized['other'] = uncategorized
        
        return categorized
    
    def count_skills(self, text: str) -> int:
        """Count number of skills in text."""
        return len(self.extract(text))


def extract_skills_from_text(text: str) -> List[str]:
    """
    Convenience function to extract skills.
    
    Args:
        text: Input text
        
    Returns:
        List of normalized skills
    """
    extractor = SkillExtractor()
    return extractor.extract(text)
