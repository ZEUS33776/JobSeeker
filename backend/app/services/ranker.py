import json
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class JobRanker:
    def __init__(self):
        """Initialize the job ranker with LangChain and Gemini AI"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.2,  # Lower temperature for more consistent ranking
                google_api_key=GEMINI_API_KEY
            )
            self.parser = JsonOutputParser()
            self._setup_prompt_template()
            # Create the LLM chain after prompt is set up
            self.llm_chain = self.ranking_prompt | self.llm | self.parser
        except Exception as e:
            logger.error(f"Failed to initialize JobRanker: {e}")
            raise

    def _setup_prompt_template(self):
        """Setup the prompt template for job ranking"""
        self.ranking_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert job matching AI that ranks job opportunities based on candidate fit.
            You MUST respond with valid JSON only. Do not include any text before or after the JSON.
            
            IMPORTANT: Only include jobs that are genuinely relevant to the candidate's skills and role.
            If a job has no skill matches and doesn't align with the candidate's role/variants, DO NOT include it in the results."""),
            ("human", """
Rank these job search results based on how well they match the candidate's profile.
Return ONLY the top {max_results_requested} most relevant jobs.

CANDIDATE PROFILE:
Skills: {skills}
Original Role: {role}
PRIORITIZED ROLES (User Selected): {role_variants}

JOB SEARCH RESULTS:
{job_results}

STRICT FILTERING CRITERIA:
- FIRST PRIORITY: Match the user's selected/prioritized roles ({role_variants})
- SECOND PRIORITY: Match skills and experience level
- If seeking tech roles, ONLY include tech-related positions
- If NO skills match and role doesn't align, EXCLUDE the job completely
- Minimum threshold: Job must score at least 50 points to be included

RANKING CRITERIA (for jobs that pass filtering):
1. ROLE ALIGNMENT (50%): How well the job matches the user's SELECTED roles ({role_variants}) - THIS IS MOST IMPORTANT
2. Skill Match (30%): How many candidate skills are relevant to the job
3. Job Quality (15%): Based on company reputation, job description quality
4. Career Relevance (5%): Overall relevance to candidate's career goals

SCORING SCALE:
- 90-100: Excellent match (perfect role + skills match)
- 80-89: Very good match (strong role alignment + good skills) 
- 70-79: Good match (role matches + some skills)
- 60-69: Fair match (partial role match + skills)
- 50-59: Minimum acceptable match
- Below 50: EXCLUDE from results

CRITICAL: If the user selected specific roles (like AI/ML roles), heavily prioritize jobs that match those roles even if they don't perfectly match the original resume role.

IMPORTANT: Return ONLY the top {max_results_requested} jobs, ranked by score (highest first).

Respond with ONLY this JSON structure (no other text):
{{
    "ranked_jobs": [
        {{
            "title": "job title",
            "url": "job url", 
            "snippet": "job snippet",
            "source": "job source",
            "score": 85,
            "reasons": ["reason1", "reason2"],
            "skill_matches": ["skill1", "skill2"],
            "role_match": "exact"
        }}
    ],
    "summary": {{
        "total_jobs": 10,
        "high_relevance": 3,
        "medium_relevance": 4,
        "low_relevance": 3
    }}
}}

Role match values: "exact", "close", "partial", "weak"
Only rank the most relevant jobs. Maximum {max_results_requested} jobs in ranked_jobs array.
        """)
        ])

    def rank_jobs(self, parsed_info: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank job search results based on resume and user requirements
        
        Args:
            parsed_info: Dictionary containing skills, role, role_variants
            search_results: Search results from Google containing job listings
            
        Returns:
            Dictionary containing ranked jobs as JSON
        """
        try:
            # Extract job listings from search results
            job_listings = self._extract_job_listings(search_results)
            
            if not job_listings:
                logger.warning("No job listings found in search results")
                return {
                    "ranked_jobs": [],
                    "summary": {
                        "total_jobs": 0,
                        "filtered_jobs": 0,
                        "high_relevance": 0,
                        "medium_relevance": 0,
                        "low_relevance": 0
                    }
                }
            
            # Prepare data for LLM - handle both old and new format
            print(f"[RANKER DEBUG] parsed_info keys: {list(parsed_info.keys())}")
            print(f"[RANKER DEBUG] parsed_info.Skills: {parsed_info.get('Skills', 'NOT_FOUND')}")
            
            skills_data = parsed_info.get("Skills", [])
            if isinstance(skills_data, list):
                skills = skills_data  # Old format
            else:
                # New format might have skills_breakdown
                skills_breakdown = parsed_info.get("skills_breakdown", {})
                if isinstance(skills_breakdown, dict):
                    skills = skills_breakdown.get("core", []) + skills_breakdown.get("secondary", [])
                else:
                    skills = []
            
            # If still no skills, try alternative keys
            if not skills:
                # Try other possible skill keys
                alt_skills = parsed_info.get("skills", []) or parsed_info.get("technical_skills", [])
                if alt_skills:
                    skills = alt_skills if isinstance(alt_skills, list) else []
                    print(f"[RANKER DEBUG] Found skills in alternative key: {skills[:5]}...")
            
            print(f"[RANKER DEBUG] Final skills extracted: {skills[:10]}...")  # Show first 10 skills
            
            role = parsed_info.get("Role", "")
            role_variants = parsed_info.get("Role_Variants", [])
            desired_roles = parsed_info.get("Desired_Roles", "")
            
            # Debug logging for role selection
            print(f"[RANKER DEBUG] Original role: {role}")
            print(f"[RANKER DEBUG] Role variants: {role_variants}")
            print(f"[RANKER DEBUG] Desired roles: {desired_roles}")
            print(f"[RANKER DEBUG] Skills: {skills[:5]}...")  # First 5 skills
            
            # Pre-filter jobs using basic relevance check
            pre_filtered_jobs = self._pre_filter_jobs(job_listings, skills, role, role_variants, parsed_info)
            
            if not pre_filtered_jobs:
                logger.warning("No relevant jobs found after pre-filtering")
                return {
                    "ranked_jobs": [],
                    "summary": {
                        "total_jobs": len(job_listings),
                        "filtered_jobs": 0,
                        "high_relevance": 0,
                        "medium_relevance": 0,
                        "low_relevance": 0
                    }
                }
            
            # Get max_results from parsed_info if available, otherwise default to 20
            max_results = parsed_info.get("max_results", 20)
            logger.info(f"Limiting results to {max_results} jobs as requested")
            
            # If we have too many pre-filtered jobs, take a diverse sample
            if len(pre_filtered_jobs) > max_results * 2:
                # Take top jobs from different sources to ensure diversity
                source_jobs = {}
                for job in pre_filtered_jobs:
                    source = job.get('source', 'unknown')
                    if source not in source_jobs:
                        source_jobs[source] = []
                    source_jobs[source].append(job)
                
                # Take proportionally from each source
                sampled_jobs = []
                jobs_per_source = max(1, (max_results * 2) // len(source_jobs))
                
                for source, jobs in source_jobs.items():
                    sampled_jobs.extend(jobs[:jobs_per_source])
                    if len(sampled_jobs) >= max_results * 2:
                        break
                
                pre_filtered_jobs = sampled_jobs[:max_results * 2]
                logger.info(f"Sampled {len(pre_filtered_jobs)} diverse jobs from {len(source_jobs)} sources")
            
            # Format jobs for LLM prompt
            formatted_jobs = self._format_jobs_for_prompt(pre_filtered_jobs)
            
            # Call LLM for ranking with max_results context
            # Combine role variants and desired roles for better matching
            all_roles = []
            if desired_roles and desired_roles.strip():
                desired_roles_list = [r.strip() for r in desired_roles.split(",") if r.strip()]
                all_roles.extend(desired_roles_list)
            if role_variants:
                all_roles.extend(role_variants)
            if role and role not in all_roles:
                all_roles.append(role)
            
            ranking_response = self.llm_chain.invoke({
                "skills": ", ".join(skills),
                "role": role,
                "role_variants": ", ".join(all_roles),
                "job_results": formatted_jobs,
                "max_results_requested": max_results
            })
            
            # Parse the response
            if isinstance(ranking_response, dict):
                ranked_jobs = ranking_response.get("ranked_jobs", [])
                summary = ranking_response.get("summary", {})
                
                # Apply max_results limit to final results
                if len(ranked_jobs) > max_results:
                    ranked_jobs = ranked_jobs[:max_results]
                    logger.info(f"Limited final results to {max_results} top-ranked jobs")
                
                # Update summary with actual counts
                summary.update({
                    "total_jobs": len(job_listings),
                    "filtered_jobs": len(pre_filtered_jobs),
                    "final_ranked": len(ranked_jobs),
                    "max_requested": max_results
                })
                
                logger.info(f"Job ranking completed: {len(ranked_jobs)} ranked jobs returned")
                
                return {
                    "ranked_jobs": ranked_jobs,
                    "summary": summary
                }
            else:
                logger.error("Invalid response format from LLM ranking")
                return {
                    "ranked_jobs": [],
                    "summary": {
                        "total_jobs": len(job_listings),
                        "filtered_jobs": len(pre_filtered_jobs),
                        "final_ranked": 0,
                        "max_requested": max_results,
                        "error": "Invalid LLM response format"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in job ranking: {e}")
            # Return fallback ranking
            return self._fallback_ranking(
                job_listings if 'job_listings' in locals() else [], 
                parsed_info if 'parsed_info' in locals() else None,
                len(job_listings) if 'job_listings' in locals() else 0
            )

    def _pre_filter_jobs(self, job_listings: List[Dict[str, Any]], skills: List[str], role: str, role_variants: List[str], parsed_info: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Pre-filter jobs to remove completely irrelevant ones"""
        if not skills and not role and not role_variants:
            return []
        
        filtered_jobs = []
        skills_lower = [skill.lower() for skill in skills]
        role_lower = role.lower() if role else ""
        role_variants_lower = [rv.lower() for rv in role_variants]
        
        # Define general tech-related keywords for better filtering
        tech_keywords = {
            'developer', 'engineer', 'programmer', 'software', 'data', 'analyst', 'scientist',
            'devops', 'frontend', 'backend', 'fullstack', 'mobile', 'web', 'cloud',
            'python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'database',
            'cybersecurity', 'network', 'system', 'admin', 'architect', 'tech', 'technology', 
            'intern', 'internship', 'manager', 'lead', 'senior', 'junior'
        }
        
        # Extract keywords dynamically from user's selected roles
        user_role_keywords = set()
        all_user_roles = [role_lower] + role_variants_lower if role_lower else role_variants_lower
        
        for user_role in all_user_roles:
            if user_role:
                # Split role into individual words and add them as keywords
                words = user_role.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
                for word in words:
                    clean_word = word.strip().lower()
                    if len(clean_word) > 2:  # Only add words longer than 2 characters
                        user_role_keywords.add(clean_word)
        
        # Check if candidate is looking for tech roles
        is_tech_candidate = any(keyword in (role_lower + " " + " ".join(role_variants_lower)) for keyword in tech_keywords)
        
        # Check user preferences for experience level (if available)
        user_experience = ""
        user_job_type = ""
        wants_senior_roles = False
        wants_internships = False
        
        if parsed_info:
            user_experience = parsed_info.get("User_Experience_Level", "").lower()
            user_job_type = parsed_info.get("User_Job_Type", "").lower()
            wants_senior_roles = user_experience == "senior"
            wants_internships = user_job_type == "internship" or "intern" in role_lower
        
        print(f"[PRE-FILTER DEBUG] Skills count: {len(skills)}")
        print(f"[PRE-FILTER DEBUG] Role variants: {role_variants_lower}")
        print(f"[PRE-FILTER DEBUG] Extracted role keywords: {list(user_role_keywords)}")
        print(f"[PRE-FILTER DEBUG] Is tech candidate: {is_tech_candidate}")
        
        for job in job_listings:
            title_lower = job['title'].lower()
            snippet_lower = job['snippet'].lower()
            combined_text = f"{title_lower} {snippet_lower}"
            
            # Check for skill matches
            skill_matches = [skill for skill in skills_lower if skill in combined_text]
            
            # Enhanced role alignment check
            role_match = False
            
            # Check exact role match in title
            if role_lower and role_lower in title_lower:
                role_match = True
            
            # Check role variants in title (more flexible matching)
            elif any(variant in title_lower for variant in role_variants_lower if variant):
                role_match = True
            
            # Check for user's role keywords in job title and content
            elif user_role_keywords:
                keyword_matches = sum(1 for keyword in user_role_keywords if keyword in combined_text)
                # If at least 1 role keyword matches, consider it a role match
                if keyword_matches >= 1:
                    role_match = True
                    print(f"[PRE-FILTER DEBUG] Role keyword match found for: {job['title'][:50]}... (matched {keyword_matches} keywords)")
            
            # For tech candidates, ensure the job is tech-related
            if is_tech_candidate:
                is_tech_job = any(keyword in combined_text for keyword in tech_keywords)
                if not is_tech_job:
                    print(f"[PRE-FILTER DEBUG] Filtered out non-tech job: {job['title'][:50]}...")
                    continue  # Skip non-tech jobs for tech candidates
            
            # Filter based on experience level preferences
            job_is_internship = any(intern_term in combined_text for intern_term in ['intern', 'internship', 'trainee'])
            job_is_senior = any(senior_term in combined_text for senior_term in ['senior', 'lead', 'principal', 'manager'])
            
            # Skip internships if user wants senior roles
            if wants_senior_roles and job_is_internship:
                print(f"[PRE-FILTER DEBUG] Filtered out internship for senior candidate: {job['title'][:50]}...")
                continue
                
            # Skip senior roles if user specifically wants internships
            if wants_internships and not job_is_internship and job_is_senior:
                print(f"[PRE-FILTER DEBUG] Filtered out senior role for internship candidate: {job['title'][:50]}...")
                continue
            
            # More lenient inclusion criteria:
            # Include job if it has skill matches OR role alignment OR matches user's role keywords
            include_job = False
            
            if skill_matches:
                include_job = True
                print(f"[PRE-FILTER DEBUG] Included job (skill match): {job['title'][:50]}... Skills: {skill_matches}")
            elif role_match:
                include_job = True
                print(f"[PRE-FILTER DEBUG] Included job (role match): {job['title'][:50]}...")
            elif user_role_keywords and any(keyword in combined_text for keyword in user_role_keywords):
                include_job = True
                print(f"[PRE-FILTER DEBUG] Included job (role keyword relevance): {job['title'][:50]}...")
            else:
                print(f"[PRE-FILTER DEBUG] Filtered out job (no relevance): {job['title'][:50]}...")
            
            if include_job:
                filtered_jobs.append(job)
        
        print(f"[PRE-FILTER DEBUG] Pre-filtered {len(filtered_jobs)} relevant jobs out of {len(job_listings)} total")
        logger.info(f"Pre-filtered {len(filtered_jobs)} relevant jobs out of {len(job_listings)} total")
        return filtered_jobs

    def _extract_job_listings(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract job listings from search results"""
        job_listings = []
        
        # Handle both formats: search_results with 'organic' key or direct list
        if 'organic' in search_results:
            for job in search_results['organic']:
                job_listings.append({
                    'title': job.get('title', ''),
                    'url': job.get('link', ''),
                    'snippet': job.get('snippet', ''),
                    'source': self._extract_source_from_url(job.get('link', ''))
                })
        
        # Also check for direct listings in search_results keys
        for key, listings in search_results.items():
            if isinstance(listings, list) and key != 'organic':
                for job in listings:
                    if isinstance(job, dict) and 'title' in job:
                        job_listings.append({
                            'title': job.get('title', ''),
                            'url': job.get('url', job.get('link', '')),
                            'snippet': job.get('snippet', ''),
                            'source': job.get('source', self._extract_source_from_url(job.get('url', job.get('link', ''))))
                        })
        
        return job_listings

    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        if not url:
            return "unknown"
        
        if "linkedin.com" in url:
            return "linkedin.com"
        elif "indeed.com" in url:
            return "indeed.com"
        elif "naukri.com" in url:
            return "naukri.com"
        elif "wellfound.com" in url:
            return "wellfound.com"
        elif "internshala.com" in url:
            return "internshala.com"
        else:
            # Extract domain
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                return domain.replace('www.', '')
            except:
                return "unknown"

    def _format_jobs_for_prompt(self, job_listings: List[Dict[str, Any]]) -> str:
        """Format job listings for the LLM prompt"""
        formatted = []
        for i, job in enumerate(job_listings, 1):
            formatted.append(f"""
{i}. **{job['title']}**
   - URL: {job['url']}
   - Source: {job['source']}
   - Description: {job['snippet']}
""")
        return "\n".join(formatted)

    def _fallback_ranking(self, job_listings: List[Dict[str, Any]], parsed_info: Dict[str, Any] = None, total_jobs: int = 0) -> Dict[str, Any]:
        """Improved fallback ranking method with strict relevance filtering"""
        if not parsed_info:
            return {
                "ranked_jobs": [],
                "summary": {
                    "total_jobs": total_jobs,
                    "filtered_jobs": 0,
                    "high_relevance": 0,
                    "medium_relevance": 0,
                    "low_relevance": 0
                }
            }
        
        ranked_jobs = []
        
        # Extract skills and role info
        skills = parsed_info.get("Skills", [])
        role = parsed_info.get("Role", "").lower()
        role_variants = [rv.lower() for rv in parsed_info.get("Role_Variants", [])]
        
        for job in job_listings:
            title_lower = job['title'].lower()
            snippet_lower = job['snippet'].lower()
            combined_text = f"{title_lower} {snippet_lower}"
            
            # Base score - start lower for stricter filtering
            score = 30
            reasons = []
            skill_matches = []
            role_match = "weak"
            
            # Skill matching (40% weight)
            for skill in skills:
                if skill.lower() in combined_text:
                    skill_matches.append(skill)
                    score += 10  # Increased points per skill match
            
            # Role matching (30% weight)
            if role and role in title_lower:
                score += 20
                role_match = "exact"
                reasons.append(f"Exact role match: {role}")
            elif any(variant in title_lower for variant in role_variants):
                score += 15
                role_match = "close"
                reasons.append("Close role variant match")
            elif "intern" in title_lower and ("intern" in role or any("intern" in rv for rv in role_variants)):
                score += 12
                role_match = "partial"
                reasons.append("Internship role match")
            
            # Only include jobs that meet minimum threshold
            if score < 50:
                continue
            
            if skill_matches:
                reasons.append(f"Matches {len(skill_matches)} skills: {', '.join(skill_matches)}")
            
            # Source quality bonus (10% weight)
            source_bonuses = {
                "linkedin.com": 5,
                "wellfound.com": 4,
                "indeed.com": 3,
                "naukri.com": 3,
                "internshala.com": 2
            }
            source_bonus = source_bonuses.get(job.get('source', ''), 0)
            if source_bonus > 0:
                score += source_bonus
                reasons.append(f"Quality source: {job.get('source', 'unknown')}")
            
            # Content quality bonus (10% weight)
            if len(job.get('snippet', '')) > 100:
                score += 3
                reasons.append("Detailed job description")
            
            if not reasons:
                reasons = ["Minimum relevance threshold met"]
            
            # Cap the score at 100
            score = min(score, 100)
            
            ranked_jobs.append({
                "title": job['title'],
                "url": job['url'],
                "snippet": job['snippet'],
                "source": job['source'],
                "score": score,
                "reasons": reasons,
                "skill_matches": skill_matches,
                "role_match": role_match
            })
        
        # Sort by score (highest first)
        ranked_jobs.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate summary
        high_relevance = len([j for j in ranked_jobs if j['score'] >= 80])
        medium_relevance = len([j for j in ranked_jobs if 60 <= j['score'] < 80])
        low_relevance = len([j for j in ranked_jobs if j['score'] < 60])
        
        return {
            "ranked_jobs": ranked_jobs,
            "summary": {
                "total_jobs": total_jobs,
                "filtered_jobs": len(ranked_jobs),
                "high_relevance": high_relevance,
                "medium_relevance": medium_relevance,
                "low_relevance": low_relevance
            }
        }


# Convenience function for easy import
def rank_job_results(parsed_info: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rank job search results based on parsed resume info and search results
    
    Args:
        parsed_info: Dictionary containing skills, role, role_variants from LLM extraction
        search_results: Search results from Google job search
        
    Returns:
        Dictionary containing ranked jobs with scores and reasoning (only relevant jobs)
    """
    ranker = JobRanker()
    return ranker.rank_jobs(parsed_info, search_results)