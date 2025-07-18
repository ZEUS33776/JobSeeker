from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import json
import os
import tempfile
import logging
from datetime import datetime

from app.services.resume_ingestor import process_resume_file
from app.services.llm_extractor import extract_resume_info
from app.services.search_engine import search_jobs
from app.services.ranker import rank_job_results
from app.services.scraper import scrape_job, get_safe_config
from app.core.config import validate_api_keys

logger = logging.getLogger(__name__)
router = APIRouter()

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

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    location: str = Form(""),  # Optional - defaults to empty string for global search
    experience_level: str = Form("entry"),  # entry, mid, senior
    job_type: str = Form("full-time"),  # full-time, part-time, internship, contract
    remote_preference: str = Form("hybrid")  # remote, on-site, hybrid
):
    """Upload and process resume with job preferences"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, DOC, or TXT files.")
        
        # Create session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process resume
            logger.info(f"Processing resume for session {session_id}")
            processed_data = process_resume_file(temp_file_path)
            
            # Extract information using LLM
            resume_info = extract_resume_info(processed_data['content'])
            
            # Get AI-suggested roles and domain analysis
            from app.services.llm_extractor import identify_skill_domains_and_roles
            domain_analysis = identify_skill_domains_and_roles(
                processed_data['content'], 
                resume_info.get("Skills", [])
            )
            
            # Store session data
            user_sessions[session_id] = {
                "resume_info": resume_info,
                "resume_text": processed_data['content'],  # Store raw resume text for analysis
                "domain_analysis": domain_analysis,  # Store AI-suggested roles and domain info
                "preferences": {
                    "location": location,
                    "experience_level": experience_level,
                    "job_type": job_type,
                    "remote_preference": remote_preference
                },
                "created_at": datetime.now(),
                "filename": file.filename
            }
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return JSONResponse({
                "success": True,
                "session_id": session_id,
                "message": "Resume processed successfully",
                "data": {
                    "extracted_info": {
                        "role": resume_info.get("Role", ""),
                        "skills": resume_info.get("Skills", []),  # All skills
                        "experience": resume_info.get("Experience", ""),
                        "total_skills": len(resume_info.get("Skills", []))
                    },
                    "ai_suggestions": {
                        "primary_roles": domain_analysis.get("primary_roles", []),
                        "secondary_roles": domain_analysis.get("secondary_roles", []),
                        "skill_domains": domain_analysis.get("domains", []),
                        "suggested_roles_detailed": domain_analysis.get("suggested_roles", []),
                        "strongest_domain": domain_analysis.get("skill_summary", {}).get("strongest_domain", ""),
                        "cross_domain_potential": domain_analysis.get("skill_summary", {}).get("cross_domain_potential", "")
                    },
                    "preferences": {
                        "location": location,
                        "experience_level": experience_level,
                        "job_type": job_type,
                        "remote_preference": remote_preference
                    }
                }
            })
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.post("/search-jobs")
async def search_jobs_endpoint(
    session_id: str = Form(...),
    additional_keywords: str = Form(""),
    max_results: int = Form(20),
    updated_skills: str = Form("")  # JSON string of updated skills from frontend
):
    """Search for jobs based on processed resume and preferences"""
    try:
        # Validate session
        if session_id not in user_sessions:
            raise HTTPException(status_code=404, detail="Session not found. Please upload your resume first.")
        
        session_data = user_sessions[session_id]
        resume_info = session_data["resume_info"]
        preferences = session_data["preferences"]
        
        # Use updated skills if provided, otherwise use original skills from resume
        if updated_skills:
            try:
                import json
                skills = json.loads(updated_skills)
                logger.info(f"Using updated skills from user: {len(skills)} skills")
            except json.JSONDecodeError:
                logger.warning("Invalid updated_skills JSON, using original skills")
                skills = resume_info.get("Skills", [])
        else:
            skills = resume_info.get("Skills", [])
        
        # Build search query based on user preferences
        role = resume_info.get("Role", "")
        location = preferences["location"] or "India"  # Default to India if no location specified
        job_type = preferences["job_type"]
        experience_level = preferences["experience_level"]
        
        # Override role based on user preferences to ensure search matches user intent
        adjusted_role = adjust_role_for_preferences(role, job_type, experience_level)
        
        # Update resume_info with adjusted role and skills for ranking consistency
        resume_info_for_ranking = resume_info.copy()
        resume_info_for_ranking["Role"] = adjusted_role
        resume_info_for_ranking["Skills"] = skills  # Use updated skills for ranking
        resume_info_for_ranking["User_Experience_Level"] = experience_level
        resume_info_for_ranking["User_Job_Type"] = job_type
        
        # Combine keywords
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
        
        logger.info(f"Role adjustment: '{role}' -> '{adjusted_role}' (experience: {experience_level}, job_type: {job_type})")
        logger.info(f"Searching jobs for query: {query}, location: {location}")
        
        # Search for jobs with user preferences
        search_results = search_jobs(
            query=query,
            location=location,
            num_results=max_results,
            experience_level=experience_level,
            job_type=job_type
        )
        
        # Rank results using adjusted role and preferences
        ranked_results = rank_job_results(resume_info_for_ranking, search_results)
        
        # Store search results in session
        user_sessions[session_id]["last_search"] = {
            "query": query,
            "results": ranked_results,
            "searched_at": datetime.now()
        }
        
        return JSONResponse({
            "success": True,
            "message": f"Found {len(ranked_results.get('ranked_jobs', []))} relevant jobs",
            "data": {
                "search_query": query,
                "location": location,
                "total_jobs_found": ranked_results.get("summary", {}).get("total_jobs", 0),
                "relevant_jobs": len(ranked_results.get("ranked_jobs", [])),
                "jobs": ranked_results.get("ranked_jobs", []),
                "summary": ranked_results.get("summary", {})
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@router.post("/fetch-job-description")
async def fetch_job_description(
    job_url: str = Form(...),
    session_id: str = Form(...)
):
    """Fetch detailed job description using the scraper"""
    try:
        # Check API keys first
        missing_keys = validate_api_keys()
        if missing_keys:
            return JSONResponse({
                "success": False,
                "message": "API configuration incomplete",
                "error": f"Missing required API keys: {', '.join(missing_keys)}. Please configure your .env file.",
                "data": {
                    "url": job_url,
                    "configuration_needed": missing_keys,
                    "attempted_at": datetime.now().isoformat()
                }
            }, status_code=503)  # Service Unavailable
        
        # Validate session (create test session if none exists)
        if session_id not in user_sessions:
            if session_id.startswith('test'):
                # Create a temporary test session for testing purposes
                user_sessions[session_id] = {
                    "resume_info": {"Role": "Test", "Skills": [], "Experience": ""},
                    "preferences": {"location": "Bengaluru"},
                    "created_at": datetime.now(),
                    "filename": "test_session.pdf"
                }
                logger.info(f"Created temporary test session: {session_id}")
            else:
                raise HTTPException(status_code=404, detail="Session not found.")
        
        # Validate URL
        if not job_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid job URL provided.")
        
        logger.info(f"Fetching job description from: {job_url}")
        
        # Use headless scraper with safe configuration
        config = get_safe_config()
        
        # Scrape job description
        result = await scrape_job(job_url, config=config, headless=True)
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": "Job description fetched successfully",
                "data": {
                    "url": result["url"],
                    "site": result["site"],
                    "title": result["title"],
                    "company": result["company"],
                    "location": result["location"],
                    "description": result["description"],
                    "description_length": len(result["description"]) if result["description"] else 0,
                    "fetched_at": datetime.now().isoformat(),
                    "proxy_used": result.get("proxy_used", "Direct connection")
                }
            })
        else:
            error_message = result.get("error", "Failed to extract job description")
            return JSONResponse({
                "success": False,
                "message": "Could not fetch job description",
                "error": error_message,
                "data": {
                    "url": result["url"],
                    "site": result.get("site", "Unknown"),
                    "attempted_at": datetime.now().isoformat()
                }
            }, status_code=422)
            
    except Exception as e:
        logger.error(f"Error fetching job description: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching job description: {str(e)}")

@router.post("/test-job-scraper")
async def test_job_scraper(
    job_url: str = Form(...)
):
    """Test endpoint for job description scraping without session requirement"""
    try:
        # Validate URL
        if not job_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid job URL provided.")
        
        logger.info(f"Testing job scraper with URL: {job_url}")
        
        # Use headless scraper with safe configuration
        config = get_safe_config()
        logger.info(f"Config created: {config}")
        
        # Scrape job description
        logger.info("Starting job scraping...")
        result = await scrape_job(job_url, config=config, headless=True)
        logger.info(f"Scraping completed. Success: {result.get('success')}")
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": "Job description scraped successfully",
                "data": {
                    "url": result["url"],
                    "site": result["site"],
                    "title": result["title"],
                    "company": result["company"],
                    "location": result["location"],
                    "description": result["description"],
                    "description_length": len(result["description"]) if result["description"] else 0,
                    "fetched_at": datetime.now().isoformat(),
                    "proxy_used": result.get("proxy_used", "Direct connection")
                }
            })
        else:
            error_message = result.get("error", "Failed to extract job description")
            logger.warning(f"Scraping failed: {error_message}")
            return JSONResponse({
                "success": False,
                "message": "Could not scrape job description",
                "error": error_message,
                "data": {
                    "url": result["url"],
                    "site": result.get("site", "Unknown"),
                    "attempted_at": datetime.now().isoformat()
                }
            }, status_code=422)
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in test job scraper: {e}")
        logger.error(f"Full traceback: {error_details}")
        
        return JSONResponse({
            "success": False,
            "message": "Internal server error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": error_details
        }, status_code=500)

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information and last search results"""
    try:
        if session_id not in user_sessions:
            raise HTTPException(status_code=404, detail="Session not found.")
        
        session_data = user_sessions[session_id]
        
        return JSONResponse({
            "success": True,
            "data": {
                "session_id": session_id,
                "filename": session_data["filename"],
                "created_at": session_data["created_at"].isoformat(),
                "resume_info": {
                    "role": session_data["resume_info"].get("Role", ""),
                    "skills_count": len(session_data["resume_info"].get("Skills", [])),
                    "experience": session_data["resume_info"].get("Experience", "")
                },
                "preferences": session_data["preferences"],
                "has_search_results": "last_search" in session_data,
                "last_search": session_data.get("last_search", {}).get("searched_at", "").isoformat() if "last_search" in session_data else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session data"""
    try:
        if session_id in user_sessions:
            del user_sessions[session_id]
            return JSONResponse({
                "success": True,
                "message": "Session deleted successfully"
            })
        else:
            raise HTTPException(status_code=404, detail="Session not found.")
            
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.post("/analyze-resume-vs-job")
async def analyze_resume_vs_job(
    session_id: str = Form(...),
    job_description: str = Form(...)
):
    """Analyze resume against job description for ATS compatibility and match analysis"""
    try:
        # Check API keys first
        missing_keys = validate_api_keys()
        if missing_keys:
            return JSONResponse({
                "success": False,
                "message": "API configuration incomplete",
                "error": f"Missing required API keys: {', '.join(missing_keys)}. Please configure your .env file.",
                "configuration_needed": missing_keys
            }, status_code=503)
        
        # Validate session
        if session_id not in user_sessions:
            raise HTTPException(status_code=404, detail="Session not found. Please upload your resume first.")
        
        # Validate job description
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
        if len(job_description.strip()) < 50:
            raise HTTPException(status_code=400, detail="Job description is too short. Please provide a detailed job description.")
        
        session_data = user_sessions[session_id]
        resume_info = session_data["resume_info"]
        
        # Get resume text from session or storage
        resume_text = session_data.get("resume_text", "")
        if not resume_text:
            # Try to get from processed data if available
            resume_text = f"Role: {resume_info.get('Role', '')}\nSkills: {', '.join(resume_info.get('Skills', []))}\nExperience: {resume_info.get('Experience', '')}"
        
        logger.info(f"Starting ATS analysis for session {session_id}")
        
        # Import the analysis function
        from app.services.llm_extractor import analyze_resume_vs_job_description
        
        # Perform detailed ATS analysis
        analysis_result = analyze_resume_vs_job_description(
            resume_text=resume_text,
            resume_info=resume_info,
            job_description=job_description
        )
        
        # Store analysis in session for potential future reference
        user_sessions[session_id]["last_analysis"] = {
            "job_description": job_description,
            "analysis_result": analysis_result,
            "analyzed_at": datetime.now()
        }
        
        return JSONResponse({
            "success": True,
            "message": "Resume analysis completed successfully",
            "data": analysis_result
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resume analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "success": True,
        "message": "Job Seeker API is running",
        "active_sessions": len(user_sessions),
        "timestamp": datetime.now().isoformat()
    })