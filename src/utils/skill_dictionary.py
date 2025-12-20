"""
Skill Dictionary - Standardization and synonym mapping for IT skills.
"""
from typing import Dict, List, Set, Optional, Tuple
import re


class SkillDictionary:
    """
    Dictionary for standardizing and matching IT skills.
    Handles synonyms, abbreviations, and variations.
    """
    
    # Canonical skill mappings (variation -> standard)
    SKILL_SYNONYMS: Dict[str, str] = {
        # Programming Languages
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "c#": "csharp",
        "c sharp": "csharp",
        "golang": "go",
        "node": "nodejs",
        "node.js": "nodejs",
        
        # Frameworks
        "react.js": "react",
        "reactjs": "react",
        "vue.js": "vue",
        "vuejs": "vue",
        "angular.js": "angular",
        "angularjs": "angular",
        "next.js": "nextjs",
        "nuxt.js": "nuxtjs",
        "express.js": "express",
        "expressjs": "express",
        "spring boot": "springboot",
        "spring-boot": "springboot",
        "fast api": "fastapi",
        "fast-api": "fastapi",
        "ruby on rails": "rails",
        "ror": "rails",
        ".net": "dotnet",
        "asp.net": "aspnet",
        
        # Databases
        "postgres": "postgresql",
        "mongo": "mongodb",
        "ms sql": "mssql",
        "sql server": "mssql",
        "microsoft sql server": "mssql",
        "mysql": "mysql",
        "maria db": "mariadb",
        
        # Cloud & DevOps
        "amazon web services": "aws",
        "google cloud": "gcp",
        "google cloud platform": "gcp",
        "azure cloud": "azure",
        "microsoft azure": "azure",
        "k8s": "kubernetes",
        "kube": "kubernetes",
        "ci/cd": "cicd",
        "ci cd": "cicd",
        
        # AI/ML
        "machine learning": "ml",
        "deep learning": "dl",
        "artificial intelligence": "ai",
        "nlp": "natural language processing",
        "tensorflow": "tf",
        "scikit-learn": "sklearn",
        "scikit learn": "sklearn",
        
        # Others
        "rest api": "restapi",
        "rest-api": "restapi",
        "restful": "restapi",
        "git hub": "github",
        "git lab": "gitlab",
        "vs code": "vscode",
        "visual studio code": "vscode",
    }
    
    # Skill categories
    SKILL_CATEGORIES: Dict[str, List[str]] = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "csharp", "cpp", "c",
            "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        ],
        "web_frontend": [
            "react", "vue", "angular", "html", "css", "sass", "tailwind",
            "bootstrap", "jquery", "nextjs", "nuxtjs", "svelte", "webpack",
        ],
        "web_backend": [
            "nodejs", "express", "django", "flask", "fastapi", "spring",
            "springboot", "rails", "laravel", "aspnet", "nestjs",
        ],
        "mobile": [
            "android", "ios", "react native", "flutter", "swift", "kotlin",
        ],
        "databases": [
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "oracle", "mssql", "sqlite",
        ],
        "cloud_platforms": [
            "aws", "azure", "gcp", "heroku", "digitalocean", "vercel",
        ],
        "devops": [
            "docker", "kubernetes", "jenkins", "gitlab", "github actions",
            "terraform", "ansible", "cicd", "prometheus", "grafana",
        ],
        "data_ml": [
            "ml", "dl", "ai", "tensorflow", "pytorch", "keras", "sklearn",
            "pandas", "numpy", "spark", "hadoop",
        ],
        "tools": [
            "git", "github", "gitlab", "jira", "linux", "bash", "nginx",
        ],
    }
    
    def __init__(self):
        """Initialize skill dictionary."""
        self.synonyms = self.SKILL_SYNONYMS.copy()
        self.categories = self.SKILL_CATEGORIES.copy()
        self._build_skill_set()
    
    def _build_skill_set(self):
        """Build a set of all known skills."""
        self.all_skills: Set[str] = set()
        self.skill_to_category: Dict[str, str] = {}
        
        for category, skills in self.categories.items():
            for skill in skills:
                self.all_skills.add(skill.lower())
                self.skill_to_category[skill.lower()] = category
    
    def normalize(self, skill: str) -> str:
        """Normalize a skill name to its canonical form."""
        # Clean and lowercase
        skill = skill.strip().lower()
        skill = re.sub(r'[^\w\s\-\.\#\+]', '', skill)
        
        # Check synonym mapping
        if skill in self.synonyms:
            return self.synonyms[skill]
        
        # Check without dots
        skill_no_dots = skill.replace(".", "")
        if skill_no_dots in self.synonyms:
            return self.synonyms[skill_no_dots]
        
        return skill
    
    def get_category(self, skill: str) -> Optional[str]:
        """Get the category of a skill."""
        normalized = self.normalize(skill)
        return self.skill_to_category.get(normalized)
    
    def is_known_skill(self, skill: str) -> bool:
        """Check if skill is in our dictionary."""
        normalized = self.normalize(skill)
        return normalized in self.all_skills
    
    def are_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are the same after normalization."""
        return self.normalize(skill1) == self.normalize(skill2)
    
    def find_matches(self,
                     cv_skills: List[str],
                     jd_skills: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Find skill matches between CV and JD.
        
        Returns:
            Tuple of (matched, missing, extra) skills
        """
        cv_normalized = {self.normalize(s) for s in cv_skills if s}
        jd_normalized = {self.normalize(s) for s in jd_skills if s}
        
        matched = list(cv_normalized & jd_normalized)
        missing = list(jd_normalized - cv_normalized)
        extra = list(cv_normalized - jd_normalized)
        
        return matched, missing, extra


# Global instance
_skill_dict = SkillDictionary()


def normalize_skill(skill: str) -> str:
    """Normalize a skill using global dictionary."""
    return _skill_dict.normalize(skill)


def are_skills_similar(skill1: str, skill2: str) -> bool:
    """Check if two skills are similar."""
    return _skill_dict.are_similar(skill1, skill2)
