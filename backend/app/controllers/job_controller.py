"""
Job Controller - Business logic for job-related operations
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from app.models import (
    JobSearchRequest, JobSearchQuery, JobDetails, JobSearchResults,
    JobDescriptionRequest, JobDescriptionData, ScraperTestRequest,
    ScraperTestResult, ScraperConfig, EnhancedJobSearchData
)
from app.services.search_engine import search_jobs
from app.services.ranker import rank_job_results
from app.services.scraper import scrape_job, get_safe_config
from app.api.routers.utils import adjust_role_for_preferences, get_experience_keywords

class JobController:
    """Controller for job-related business logic"""
    
    @staticmethod
    def validate_session_for_search(session_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate session data for job search"""
        try:
            if not session_data:
                raise HTTPException(status_code=404, detail="Session not found")
            
            required_fields = ["resume_info", "preferences"]
            for field in required_fields:
                if field not in session_data:
                    raise HTTPException(status_code=500, detail=f"Missing {field}")
            
            return session_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def parse_updated_skills(updated_skills_json: str, original_skills: List[str]) -> List[str]:
        """
        Parse updated skills from JSON string
        
        Args:
            updated_skills_json: JSON string of updated skills
            original_skills: Original skills from resume
            
        Returns:
            List of skills to use
        """
        if not updated_skills_json:
            return original_skills
        
        try:
            skills = json.loads(updated_skills_json)
            if isinstance(skills, list):
                return skills
        except json.JSONDecodeError:
            pass
        
        return original_skills
    
    @staticmethod
    def build_search_query(
        session_data: Dict[str, Any],
        additional_keywords: str,
        updated_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Build job search query from session data and additional parameters
        
        Args:
            session_data: Session data containing resume info and preferences
            additional_keywords: Additional search keywords
            updated_skills: Updated skills list
            
        Returns:
            Dictionary containing search parameters
        """
        resume_info = session_data["resume_info"]
        preferences = session_data["preferences"]
        
        # Extract search parameters
        role = resume_info.get("Role", "")
        location = preferences["location"] or "India"
        job_type = preferences["job_type"]
        experience_level = preferences["experience_level"]
        
        # Adjust role based on user preferences
        adjusted_role = adjust_role_for_preferences(role, job_type, experience_level)
        
        # Build search keywords
        search_keywords = []
        if adjusted_role:
            search_keywords.append(adjusted_role)
        if additional_keywords:
            search_keywords.extend(additional_keywords.split(","))
        
        # Add experience level specific terms
        experience_keywords = get_experience_keywords(experience_level, job_type)
        if experience_keywords:
            search_keywords.extend(experience_keywords)
        
        query = " ".join(search_keywords).strip()
        
        return {
            "query": query,
            "location": location,
            "adjusted_role": adjusted_role,
            "original_role": role,
            "experience_level": experience_level,
            "job_type": job_type,
            "skills": updated_skills
        }
    
    @staticmethod
    def search_and_rank_jobs(
        search_params: Dict[str, Any],
        max_results: int,
        session_data: Dict[str, Any]
    ) -> JobSearchResults:
        """Search for jobs and rank them based on resume match"""
        try:
            # Perform job search
            search_results = search_jobs(
                query=search_params["query"],
                location=search_params["location"],
                num_results=max_results,
                experience_level=search_params["experience_level"],
                job_type=search_params["job_type"]
            )
            
            # Prepare resume info for ranking
            resume_info_for_ranking = session_data["resume_info"].copy()
            resume_info_for_ranking["Role"] = search_params["adjusted_role"]
            resume_info_for_ranking["Skills"] = search_params["skills"]
            resume_info_for_ranking["User_Experience_Level"] = search_params["experience_level"]
            resume_info_for_ranking["User_Job_Type"] = search_params["job_type"]
            
            # Rank results
            return rank_job_results(resume_info_for_ranking, search_results)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")
    
    @staticmethod
    def format_search_response(
        ranked_results: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format job search results for API response
        
        Args:
            ranked_results: Ranked job search results
            search_params: Search parameters used
            
        Returns:
            Formatted response data
        """
        jobs_count = len(ranked_results.get('ranked_jobs', []))
        
        return {
            "search_query": search_params["query"],
            "location": search_params["location"],
            "total_jobs_found": ranked_results.get("summary", {}).get("total_jobs", 0),
            "relevant_jobs": jobs_count,
            "jobs": ranked_results.get("ranked_jobs", []),
            "summary": ranked_results.get("summary", {}),
            "search_metadata": {
                "original_role": search_params["original_role"],
                "adjusted_role": search_params["adjusted_role"],
                "experience_level": search_params["experience_level"],
                "job_type": search_params["job_type"],
                "skills_count": len(search_params["skills"])
            }
        }
    
    @staticmethod
    def validate_job_url(url: str) -> str:
        """
        Validate and normalize job URL
        
        Args:
            url: Job URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            HTTPException: If URL is invalid
        """
        if not url or not url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid job URL provided"
            )
        return url.strip()
    
    @staticmethod
    def fetch_job_description(job_url: str) -> JobDescriptionData:
        """Fetch detailed job description from URL"""
        try:
            # Get scraper configuration and scrape job details
            job_data = scrape_job(job_url, get_safe_config())
            
            if not job_data or not job_data.get("description"):
                raise HTTPException(status_code=404, detail="Job description not found")
            
            return JobDescriptionData(
                title=job_data.get("title", "Job Title Not Found"),
                company=job_data.get("company", "Company Not Found"),
                location=job_data.get("location", "Location Not Found"),
                description=job_data.get("description", ""),
                url=job_url
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching job description: {str(e)}")
    
    @staticmethod
    def test_job_scraper(test_url: str) -> ScraperTestResult:
        """Test job scraper with a specific URL"""
        try:
            # Validate URL
            if not test_url or not test_url.startswith(('http://', 'https://')):
                raise HTTPException(status_code=400, detail="Invalid URL format")
            
            # Test scraping
            start_time = datetime.now()
            scraper_config = get_safe_config()
            result = scrape_job(test_url, scraper_config)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ScraperTestResult(
                url=test_url,
                success=result is not None,
                result=JobDetails(**result) if result else None,
                config_used=ScraperConfig(**scraper_config),
                execution_time=execution_time,
                error=None if result else "No data extracted"
            )
            
        except Exception as e:
            return ScraperTestResult(
                url=test_url,
                success=False,
                result=None,
                config_used=ScraperConfig(),
                error=str(e)
            )
    
    @staticmethod
    def store_search_results(
        session_id: str,
        search_params: Dict[str, Any],
        ranked_results: Dict[str, Any],
        user_sessions: Dict[str, Any]
    ) -> None:
        """Store search results in session"""
        try:
            user_sessions[session_id]["last_search"] = {
                "query": search_params["query"],
                "results": ranked_results,
                "searched_at": datetime.now(),
                "search_metadata": {
                    "location": search_params["location"],
                    "experience_level": search_params["experience_level"],
                    "job_type": search_params["job_type"],
                    "total_results": len(ranked_results.get('ranked_jobs', []))
                }
            }
        except Exception:
            pass  # Don't raise exception as this is not critical 