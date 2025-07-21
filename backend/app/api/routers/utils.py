"""
Shared utilities for API routers
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory storage for demo (use database in production)
user_sessions = {}

def adjust_role_for_preferences(original_role: str, job_type: str, experience_level: str) -> str:
    """
    Adjust the role based on user preferences - simplified for better search results
    
    Args:
        original_role: Role inferred from resume analysis
        job_type: User's preferred job type (full-time, part-time, internship, contract)
        experience_level: User's preferred experience level (entry, mid, senior)
    
    Returns:
        Simple, searchable role that respects user preferences
    """
    # Determine base role category
    role_lower = original_role.lower()
    
    # If user specifically wants internship
    if job_type == "internship":
        if "software" in role_lower or "developer" in role_lower or "engineer" in role_lower:
            return "Software Engineering Intern"
        elif "data" in role_lower:
            return "Data Science Intern"
        else:
            return "Intern"
    
    # For non-internship jobs, create simple role names
    if "software" in role_lower or "developer" in role_lower or "engineer" in role_lower:
        if experience_level == "senior":
            return "SDE III"  # Senior SDE level
        elif experience_level == "mid":
            return "SDE II"   # Mid-level SDE
        else:
            return "SDE"      # Entry-level SDE
    
    elif "data" in role_lower:
        if experience_level == "senior":
            return "Senior Data Scientist"
        elif experience_level == "mid":
            return "Data Scientist"
        else:
            return "Data Analyst"
    
    elif any(term in role_lower for term in ["ai", "ml", "machine learning", "artificial intelligence"]):
        if experience_level == "senior":
            return "Senior AI Engineer"
        elif experience_level == "mid":
            return "AI Engineer"
        else:
            return "ML Engineer"
    
    # Default fallback
    if experience_level == "senior":
        return "Senior Software Engineer"
    elif experience_level == "mid":
        return "Software Engineer"
    else:
        return "Software Developer"

def get_experience_keywords(experience_level: str, job_type: str) -> list:
    """
    Get minimal additional keywords based on experience level and job type
    Keep it simple to avoid over-specific searches
    
    Args:
        experience_level: User's preferred experience level
        job_type: User's preferred job type
    
    Returns:
        List of minimal additional keywords to include in search
    """
    keywords = []
    
    # Only add keywords for specific cases, keep it minimal
    if job_type == "internship":
        keywords.append("intern")
    
    # Don't add experience level keywords here as they're handled in search_engine.py
    # This avoids making queries too complex
    
    return keywords 