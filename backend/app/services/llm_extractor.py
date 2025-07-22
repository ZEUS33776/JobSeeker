import os
import re
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import GEMINI_API_KEY

# In-memory cache for extracted resume data
_resume_cache = {}
_domain_cache = {}

def _generate_content_hash(content: str) -> str:
    """Generate a hash for content to use as cache key"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def _is_cache_valid(cache_entry: Dict[str, Any], max_age_hours: int = 24) -> bool:
    """Check if cache entry is still valid"""
    if not cache_entry or 'timestamp' not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    age = datetime.now() - cache_time
    return age < timedelta(hours=max_age_hours)

def _get_cached_resume_info(content: str) -> Optional[Dict[str, Any]]:
    """Get cached resume info if available and valid"""
    content_hash = _generate_content_hash(content)
    if content_hash in _resume_cache:
        cache_entry = _resume_cache[content_hash]
        if _is_cache_valid(cache_entry):
            print(f"[CACHE HIT] Using cached resume extraction for hash {content_hash[:8]}...")
            return cache_entry['data']
        else:
            print(f"[CACHE EXPIRED] Removing expired cache for hash {content_hash[:8]}...")
            del _resume_cache[content_hash]
    return None

def _cache_resume_info(content: str, extracted_info: Dict[str, Any]) -> None:
    """Cache extracted resume info"""
    content_hash = _generate_content_hash(content)
    _resume_cache[content_hash] = {
        'data': extracted_info,
        'timestamp': datetime.now().isoformat(),
        'content_preview': content[:100] + "..." if len(content) > 100 else content
    }
    print(f"[CACHE STORED] Cached resume extraction for hash {content_hash[:8]}...")

def _get_cached_domain_analysis(content: str, skills: List[str]) -> Optional[Dict[str, Any]]:
    """Get cached domain analysis if available and valid"""
    # Create a combined hash for content + skills for domain analysis
    combined_content = content + "|" + ",".join(sorted(skills))
    content_hash = _generate_content_hash(combined_content)
    
    if content_hash in _domain_cache:
        cache_entry = _domain_cache[content_hash]
        if _is_cache_valid(cache_entry):
            print(f"[CACHE HIT] Using cached domain analysis for hash {content_hash[:8]}...")
            return cache_entry['data']
        else:
            print(f"[CACHE EXPIRED] Removing expired domain cache for hash {content_hash[:8]}...")
            del _domain_cache[content_hash]
    return None

def _cache_domain_analysis(content: str, skills: List[str], analysis: Dict[str, Any]) -> None:
    """Cache domain analysis"""
    combined_content = content + "|" + ",".join(sorted(skills))
    content_hash = _generate_content_hash(combined_content)
    
    _domain_cache[content_hash] = {
        'data': analysis,
        'timestamp': datetime.now().isoformat(),
        'skills_count': len(skills),
        'content_preview': content[:100] + "..." if len(content) > 100 else content
    }
    print(f"[CACHE STORED] Cached domain analysis for hash {content_hash[:8]}...")

def clear_cache(max_age_hours: int = 0) -> Dict[str, int]:
    """Clear old cache entries or all if max_age_hours=0"""
    global _resume_cache, _domain_cache
    
    removed_counts = {'resume_cache': 0, 'domain_cache': 0}
    
    if max_age_hours == 0:
        # Clear all
        removed_counts['resume_cache'] = len(_resume_cache)
        removed_counts['domain_cache'] = len(_domain_cache)
        _resume_cache.clear()
        _domain_cache.clear()
        print("[CACHE] Cleared all cache entries")
    else:
        # Clear expired entries
        current_time = datetime.now()
        
        # Clear expired resume cache
        expired_resume_keys = []
        for key, entry in _resume_cache.items():
            if not _is_cache_valid(entry, max_age_hours):
                expired_resume_keys.append(key)
        
        for key in expired_resume_keys:
            del _resume_cache[key]
            removed_counts['resume_cache'] += 1
        
        # Clear expired domain cache
        expired_domain_keys = []
        for key, entry in _domain_cache.items():
            if not _is_cache_valid(entry, max_age_hours):
                expired_domain_keys.append(key)
        
        for key in expired_domain_keys:
            del _domain_cache[key]
            removed_counts['domain_cache'] += 1
        
        print(f"[CACHE] Removed {removed_counts['resume_cache']} resume cache and {removed_counts['domain_cache']} domain cache entries")
    
    return removed_counts

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        'resume_cache_size': len(_resume_cache),
        'domain_cache_size': len(_domain_cache),
        'total_cache_entries': len(_resume_cache) + len(_domain_cache),
        'resume_cache_keys': list(_resume_cache.keys()),
        'domain_cache_keys': list(_domain_cache.keys())
    }

# Domain Analysis Prompt Template

def identify_skill_domains_and_roles(resume_content: str, extracted_skills: list) -> dict:
    """
    Analyze skills from resume and map them to specific tech domains and roles
    
    Args:
        resume_content: Text content of the resume
        extracted_skills: List of skills extracted from resume
        
    Returns:
        dict: Dictionary containing domain mapping and suggested roles
    """
    try:
        if not resume_content or not extracted_skills:
            return {
                "identified_domains": [],
                "suggested_roles": [],
                "primary_role_recommendations": [],
                "secondary_role_options": [],
                "skill_domain_summary": {},
                "role_mapping": {}
            }
        
        # Check cache first
        cached_analysis = _get_cached_domain_analysis(resume_content, extracted_skills)
        if cached_analysis:
            return cached_analysis
        
        print(f"[DOMAIN ANALYSIS] Processing new domain analysis (cache miss)...")
        
        # Create skill domain analysis prompt
        domain_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert tech recruiter who specializes in mapping candidate skills to specific tech domains and job roles."),
            ("human", """
Analyze the following resume content and skills to identify which tech domains they belong to and suggest matching job roles.

**Resume Content:**
{resume_content}

**Extracted Skills:**
{skills_list}

**Tech Domains & Associated Roles:**

🚀 **Software Development & Engineering**
- Frontend Developer (React, Angular, Vue.js, JavaScript, HTML, CSS, TypeScript)
- Backend Developer (Node.js, Django, FastAPI, Spring Boot, Java, Python, .NET)
- Full Stack Developer
- Mobile App Developer (Android, iOS, Flutter, React Native, Swift, Kotlin)
- Embedded Software Engineer (C, C++, Arduino, Raspberry Pi)
- Desktop Application Developer (.NET, JavaFX, Electron, Qt)

🧠 **Artificial Intelligence & Data Science**
- Machine Learning Engineer (TensorFlow, PyTorch, Scikit-learn, Keras)
- Data Scientist (Python, R, Statistics, Pandas, NumPy)
- AI Researcher
- Deep Learning Engineer (Neural Networks, CNN, RNN, Transformers)
- Computer Vision Engineer (OpenCV, PIL, Image Processing)
- NLP Engineer (NLTK, spaCy, Transformers, LLMs)
- Prompt Engineer
- AI Engineer (LLMs, GenAI, GPT, Claude)

📊 **Data Engineering & Analytics**
- Data Engineer (ETL pipelines, Spark, Airflow, Kafka, Hadoop)
- Data Analyst (SQL, Tableau, Power BI, Excel, Analytics)
- Business Intelligence Engineer (BI Tools, Dashboards, Reporting)
- Big Data Engineer (Hadoop, Kafka, Cassandra, MongoDB)
- Analytics Engineer

🏗️ **DevOps & Infrastructure**
- DevOps Engineer (CI/CD, Jenkins, Docker, Kubernetes, Git)
- Site Reliability Engineer (SRE)
- Cloud Engineer (AWS, GCP, Azure, Terraform, CloudFormation)
- Infrastructure Engineer
- Platform Engineer

🌐 **Web & Cloud Technologies**
- Web Developer (HTML, CSS, JavaScript, PHP, WordPress)
- Cloud Solutions Architect (AWS, Azure, GCP, Microservices)
- Cloud Security Engineer
- Serverless Application Developer (Lambda, Functions, Serverless)

🔒 **Cybersecurity**
- Security Analyst
- Security Engineer (Firewalls, VPN, Encryption)
- Penetration Tester / Ethical Hacker (Kali Linux, Metasploit)
- Security Operations Center (SOC) Analyst
- Application Security Engineer

📱 **Product & Design**
- Product Manager (Technical PM, AI PM)
- UX/UI Designer (Figma, Sketch, Adobe XD)
- Interaction Designer
- User Researcher

🧪 **Quality Assurance & Testing**
- QA Engineer (Manual/Automation Testing)
- SDET (Software Development Engineer in Test)
- Test Automation Engineer (Selenium, Cypress, Jest)
- Performance Test Engineer

⚙️ **Systems & Hardware**
- Systems Engineer
- Firmware Engineer (C, Assembly, Embedded Systems)
- Hardware Engineer
- Network Engineer (Networking, Protocols, CCNA)

🧩 **Other Specialized Tech Roles**
- Blockchain Developer (Solidity, Web3, Ethereum)
- Robotics Engineer (ROS, Robotics, Control Systems)
- Game Developer (Unity, Unreal Engine, C#, Game Development)
- AR/VR Developer (Unity, AR/VR, 3D Graphics)
- Tech Support Engineer
- Sales Engineer / Solutions Engineer

**Fallback/General Tech Domains (use these if no strong match above and add a few of your own which are also relevant but not mentioned):**
- QA Engineer
- Technical Support Engineer
- Product Manager
- Business Analyst
- IT Consultant
- Systems Administrator
- Project Coordinator
- UI/UX Designer
- Network Engineer
- Sales Engineer
- General IT/Tech Roles

**Your Task:**
1. **Domain Identification**: Map the candidate's skills to the most relevant tech domains above
2. **Role Matching**: Identify 3-7 specific job roles that best match their skill profile
3. **Confidence Scoring**: Rate how well they match each suggested role (1-10 scale)
4. **Skill Gap Analysis**: Identify what skills they might be missing for better role fit

**Guidelines:**
- Focus on the strongest skill matches
- Consider skill combinations (e.g., React + Node.js = Full Stack Developer)
- Prioritize roles where they have 60%+ of required skills
- Include both primary and secondary role options
- Consider experience level from resume content
- If the skills do not align with any of the main domains above, you MUST pick from the Fallback/General Tech Domains above, and suggest the most relevant domain(s) and roles where jobs exist for those skills, even if the match is weak or partial. Do NOT return an empty list. Always return at least one domain and 2+ roles that exist in the job market.

**Example:**
If the candidate's skills are ['Excel', 'Customer Service', 'Documentation'], you might return:
"identified_domains": [
  {{"domain": "General Tech & IT", "matching_skills": ["Excel", "Documentation"], "confidence": "low"}}
],
"suggested_roles": [
  {{"role": "Technical Support Engineer", "domain": "General Tech & IT", "matching_skills": ["Customer Service", "Documentation"], "confidence_score": 5, "role_level": "entry", "missing_skills": ["IT troubleshooting"]}},
  {{"role": "Project Coordinator", "domain": "General Tech & IT", "matching_skills": ["Documentation"], "confidence_score": 4, "role_level": "entry", "missing_skills": ["Project Management"]}}
]

**Response Format (JSON only):**
{{
    "identified_domains": [
        {{
            "domain": "Domain name (e.g., Software Development & Engineering)",
            "matching_skills": ["List of candidate's skills that fit this domain"],
            "confidence": "high/medium/low based on skill relevance"
        }}
    ],
    "suggested_roles": [
        {{
            "role": "Specific role title (e.g., Frontend Developer)",
            "domain": "Which domain this role belongs to",
            "matching_skills": ["Skills that qualify for this role"],
            "confidence_score": "1-10 rating",
            "role_level": "junior/mid/senior based on skills and experience",
            "missing_skills": ["Key skills they lack for this role"]
        }}
    ],
    "primary_role_recommendations": [
        "Top 3 roles they're best suited for (just role names)"
    ],
    "secondary_role_options": [
        "Additional 2-4 roles they could pursue (just role names)"
    ],
    "skill_domain_summary": {{
        "strongest_domain": "Domain where they have most skills",
        "secondary_domains": ["Other domains they have skills in"],
        "cross_domain_potential": "Whether they can work across multiple domains"
    }}
}}
""")
        ])
        
        # Create chain for domain analysis
        domain_chain = domain_analysis_prompt | llm | parser
        
        # Format skills for analysis
        skills_text = ", ".join(extracted_skills) if extracted_skills else "None"
        
        # Analyze domains and roles
        print(f"[DOMAIN ANALYSIS] Analyzing skills: {skills_text[:100]}...")
        domain_result = domain_chain.invoke({
            "resume_content": resume_content,
            "skills_list": skills_text
        })
        
        # Extract role suggestions
        primary_roles = domain_result.get("primary_role_recommendations", [])
        secondary_roles = domain_result.get("secondary_role_options", [])
        
        print(f"[DOMAIN ANALYSIS] Primary roles identified: {primary_roles}")
        print(f"[DOMAIN ANALYSIS] Secondary roles identified: {secondary_roles}")
        
        result = {
            "identified_domains": domain_result.get("identified_domains", []),  # Changed from "domains"
            "suggested_roles": domain_result.get("suggested_roles", []),
            "primary_role_recommendations": primary_roles,  # Changed from "primary_roles"
            "secondary_role_options": secondary_roles,  # Changed from "secondary_roles"
            "skill_domain_summary": domain_result.get("skill_domain_summary", {}),  # Changed from "skill_summary"
            "role_mapping": domain_result
        }
        
        # Cache the result
        _cache_domain_analysis(resume_content, extracted_skills, result)
        
        return result
        
    except Exception as e:
        print(f"[DOMAIN ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
        return {
            "identified_domains": [],  # Changed from "domains"
            "suggested_roles": [],
            "primary_role_recommendations": [],  # Changed from "primary_roles"
            "secondary_role_options": [],  # Changed from "secondary_roles"
            "skill_domain_summary": {},  # Changed from "skill_summary"
            "role_mapping": {}
        }

def extract_resume_info(resume_content: str) -> dict:
    """
    Extract basic resume information like role, skills, and experience from resume content
    This function actually analyzes the resume to determine the role instead of using placeholders
    
    Args:
        resume_content: Text content of the resume
        
    Returns:
        dict: Dictionary containing Role, Skills, and Experience
    """
    try:
        if not resume_content or not isinstance(resume_content, str):
            return {
                "Role": "",
                "Skills": [],
                "Experience": ""
            }
        
        # Check cache first
        cached_info = _get_cached_resume_info(resume_content)
        if cached_info:
            return cached_info
        
        print(f"[RESUME ANALYSIS] Processing new resume content (cache miss)...")
        
        # Create a proper resume analysis prompt to determine role from content
        resume_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert resume analyzer. Analyze the resume content and extract the candidate's target role, skills, and experience level."),
            ("human", """
Analyze this resume and extract key information:

**Resume Content:**
{resume_content}

**Your Task:**
1. **Determine Target Role**: Based on the resume content, what role is this person most suited for? Look at their experience, skills, and any stated objectives.
2. **Extract Skills**: List all technical skills mentioned (programming languages, tools, frameworks, technologies)
3. **Assess Experience Level**: Determine their experience level based on work history, projects, and stated experience

**Guidelines:**
- If the resume mentions "intern", "internship", or is clearly a student resume → Role should be "[Field] Intern" 
- If the resume shows development/programming skills → Role could be "Software Developer", "Frontend Developer", "Backend Developer", etc.
- If the resume shows data analysis skills → Role could be "Data Analyst", "Data Scientist", etc.
- If unclear, infer the most likely role from their strongest skills

**Response Format (JSON only):**
{{
    "target_role": "Most suitable role title",
    "skills": ["skill1", "skill2", "skill3", "..."],
    "experience_level": "fresher/entry-level/mid-level/senior",
    "role_category": "software_development/data_science/design/marketing/etc"
}}

Respond with ONLY the JSON, no other text.
""")
        ])
        
        # Create chain for resume analysis
        resume_chain = resume_analysis_prompt | llm | parser
        
        # Analyze the resume
        analysis_result = resume_chain.invoke({
            "resume_content": resume_content
        })
        
        # Extract information from analysis
        target_role = analysis_result.get("target_role", "")
        skills = analysis_result.get("skills", [])
        experience_level = analysis_result.get("experience_level", "")
        
        print(f"[RESUME ANALYSIS] Detected Role: {target_role}")
        print(f"[RESUME ANALYSIS] Detected Skills: {skills[:5]}...")  # Show first 5 skills
        print(f"[RESUME ANALYSIS] Experience Level: {experience_level}")
        
        result = {
            "Role": target_role,
            "Skills": skills,
            "Experience": experience_level
        }
        
        # Cache the result
        _cache_resume_info(resume_content, result)
        
        return result
        
    except Exception as e:
        print(f"[EXTRACT_RESUME_INFO ERROR] {type(e).__name__}: {str(e)}")
        print(f"[EXTRACT_RESUME_INFO ERROR] Full error: {str(e)}")
        # Return empty structure on error
        return {
            "Role": "",
            "Skills": [],
            "Experience": ""
        }

# Step 1: Setup Gemini with LangChain
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GEMINI_API_KEY
    )
    genai.list_models()
except Exception as e:
    raise

# Step 2: Output parser
try:
    parser = JsonOutputParser()
except Exception as e:
    raise

# Step 3: Improved Prompt Template with better search strategy
try:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a job search optimization expert specializing in creating effective search queries for maximum job discovery."),
        ("human", """
You are helping a user find the most relevant tech jobs based on their resume and preferred role: **"{role}"**.

**DOMAIN ANALYSIS RESULTS:**
- **AI-Suggested Primary Roles**: {suggested_roles}
- **Extracted Skills**: {primary_skills}
- **Skill Domain Summary**: {domain_info}

---
**Your Tasks:**

1. **Extract Skills**: Identify 8-10 technical skills from the resume, categorized as:
   - **Core Skills** (3-4): Most important/frequent skills
   - **Secondary Skills** (4-6): Supporting/complementary skills

2. **Enhanced Role Processing**: Use both user role and AI-suggested roles:
   - **Primary Focus**: User role "{role}"
   - **Enhanced Targeting**: Include AI-suggested roles: {suggested_roles}
   - **Role Expansion**: Create variations based on skill domains
   - **Experience Alignment**: Match role level to candidate experience

3. **Generate Role Variations**: Create 4-6 alternative job titles/roles combining:
   - User-specified role variations
   - AI-suggested domain-specific roles
   - Skill-based role recommendations

4. **Create 8-10 Strategic Search Queries** using AI-suggested roles WITHOUT quotes:

---
**Role Processing Guidelines:**

🎯 **For Intern Roles:**
- Input: "Software Engineering Intern" → Use: "Intern", "Internship", "Trainee"
- Include: "Summer Intern", "Winter Intern", "Developer Intern"
- Add experience terms: "fresher", "entry level", "graduate trainee"

🎯 **For SDE/Developer Roles:**
- Input: "SDE" → Use: "Software Developer", "Developer", "Engineer", "SDE"
- Include: "Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer"
- Add level terms: "SDE-1", "Junior Developer", "Associate Engineer"

🎯 **For Vague/Generic Roles:**
- Input: "Tech Role" → Infer from resume skills
- Frontend skills → "Frontend Developer", "UI Developer", "React Developer"
- Backend skills → "Backend Developer", "API Developer", "Node.js Developer"
- Full-stack skills → "Full Stack Developer", "MEAN Stack Developer"

🎯 **For Specific Tech Roles:**
- Input: "React Developer" → Use: "Frontend Developer", "React Developer", "UI Developer"
- Input: "Data Scientist" → Use: "Data Scientist", "ML Engineer", "Data Analyst"

---
**Search Query Strategy:**

**Query Types to Generate:**
1. **Primary User Role**: `site:linkedin.com/jobs "{role}" {location}`
2. **AI-Suggested Role 1**: `site:naukri.com {ai_suggested_role_1} {location}` *(NO QUOTES around AI role)*
3. **AI-Suggested Role 2**: `site:indeed.com {ai_suggested_role_2} {location}` *(NO QUOTES around AI role)*
4. **AI-Suggested Role 3**: `site:wellfound.com {ai_suggested_role_3} {location}` *(NO QUOTES around AI role)*
5. **Skills + AI Role**: `site:linkedin.com/jobs {ai_suggested_role} AND {skill1} AND {skill2} {location}`
6. **Tech Stack Query**: `site:naukri.com {skill1} {skill2} {skill3} {location}`
7. **Experience-Level + AI Role**: `site:indeed.com {ai_suggested_role} {experience_keywords} {location}`
8. **Domain-Specific Role**: `site:wellfound.com {domain_specific_role} {location}` *(NO QUOTES)*
9. **Cross-Platform AI Role**: `site:linkedin.com/jobs {ai_suggested_role} OR {alternative_ai_role} {location}`
10. **Intern-Specific Query (if applicable)**: `site:internshala.com {internship_role} {location}` *(NO QUOTES)*

**Guidelines:**
✅ **CRITICAL: AI-Suggested Roles Usage**
   - **USER ROLE**: Keep in quotes → "{role}"
   - **AI-SUGGESTED ROLES**: NO QUOTES → Frontend Developer, Backend Developer, Data Scientist
   - **Example Good**: `site:naukri.com Frontend Developer Bengaluru`
   - **Example Bad**: `site:naukri.com "Frontend Developer" Bengaluru`

✅ **Role Terms**: Use AI analysis + strategic role processing
   - **Use AI-suggested roles from domain analysis**: {suggested_roles}
   - **For Interns**: Internship, Trainee, Graduate Trainee (no quotes)
   - **For SDE**: Software Developer, Engineer, SDE, Software Engineer (no quotes)
   - **For Specific Tech**: React Developer, Python Developer, Data Scientist (no quotes)
   - ❌ Avoid: Long role descriptions with multiple qualifiers

✅ **Role-Specific Platforms**:
   - **Internships**: Include internshala.com, linkedin.com/jobs, naukri.com
   - **Developer Roles**: Focus on linkedin.com/jobs, naukri.com, indeed.com
   - **Specialized Roles**: Add wellfound.com, naukri.com

✅ **Experience-Level Keywords**:
   - **Intern/Entry**: "fresher", "entry level", "graduate", "trainee", "junior"
   - **Mid-Level**: "2-3 years", "associate", "mid level"
   - **Senior**: "senior", "lead", "3+ years", "experienced"

✅ **Skill Combinations**: 
   - Use 2-3 skills max per query with AND
   - **Frontend**: React AND JavaScript, Vue AND CSS
   - **Backend**: Node.js AND MongoDB, Python AND Django
   - **Full-Stack**: React AND Node.js, MEAN AND Stack
   - **Data**: Python AND SQL, Machine Learning AND TensorFlow

✅ **Job Board Optimization**: 
   - **LinkedIn**: Better for "Software Engineer", "Developer", company names
   - **Naukri**: Good for "SDE", skill combinations, salary terms
   - **Indeed**: Works well with broader terms, location-specific
   - **Internshala**: Essential for internship roles
   - **Wellfound**: Good for startup roles, tech companies

✅ **Location Handling**:
   - Add location at the end without quotes
   - Use variants: "Bengaluru Bangalore", "Mumbai", "Delhi NCR", "Hyderabad"
   - For remote: add "remote" or "work from home"

---
**Enhanced Output Format:**

```json
{{
  "role": "Primary role from input",
  "role_category": "intern/sde/developer/data_scientist/analyst/etc",
  "role_variants": ["Alternative role 1", "Alternative role 2", "Alternative role 3", "Alternative role 4"],
  "skills": {{
    "core": ["Top 3-4 most important skills"],
    "secondary": ["Supporting 4-6 skills"]
  }},
  "experience_level": "Detected level (fresher/junior/mid/senior)",
  "recommended_platforms": ["Best job boards for this role type"],
  "queries": [
    {{
      "query": "Complete search query",
      "type": "Query strategy type",
      "job_board": "Target job board",
      "focus": "What this query targets",
      "role_match": "Which role variant this targets"
    }}
  ]
}}
```

---
**Special Instructions for Common Roles:**

📋 **If role contains "intern":**
- MUST include internshala.com queries
- Use terms: "intern", "internship", "trainee", "summer intern"
- Add experience terms: "fresher", "entry level", "graduate"
- Focus on: learning opportunities, training programs

📋 **If role contains "sde" or "software engineer":**
- Prioritize linkedin.com/jobs and naukri.com
- Use terms: "SDE", "Software Engineer", "Developer", "SDE-1", "SDE-2"
- Include level-specific terms based on experience
- Focus on: technical skills, programming languages

📋 **If role is domain-specific (e.g., "Data Scientist"):**
- Include specialized platforms if available
- Use domain terms: "Data Scientist", "ML Engineer", "Data Analyst"
- Focus on: domain-specific skills, tools, frameworks

📋 **If role is vague/generic:**
- Infer specific roles from resume skills
- Create multiple specific variants
- Use broader search terms initially

---
**Resume Content:**
{resume}

**Additional Context:**
- Location: {location}
- Salary Range: {salary}
- Focus on creating diverse queries that cast a wide net while maintaining relevance
- Consider the user's experience level when crafting queries
- Include both technical and soft skills where appropriate
""")
    ])
except Exception as e:
    raise

# Step 4: Enhanced salary string generator
def generate_salary_string(min_salary: int, salary_type: str = "monthly") -> str:
    try:
        if not isinstance(min_salary, int) or min_salary <= 0:
            return ""
        
        if salary_type == "monthly":
            # Generate range around the min salary
            salaries = [f"₹{min_salary + i * 5000}" for i in range(-1, 2)]
            return f"salary {' OR '.join(salaries)}"
        else:
            # Generate LPA range
            salaries = [f'"{min_salary + i} LPA"' for i in range(0, 3)]
            return f"salary {' OR '.join(salaries)}"
    except Exception:
        return ""

# Step 5: Enhanced core function
def extract_keywords_from_llm(resume: str, role: str, min_salary: int = None, location: str = "Bengaluru", salary_type: str = "monthly") -> dict:
    try:
        if not resume or not isinstance(resume, str):
            return {}
        if not location or not isinstance(location, str):
            location = "Bengaluru"

        # Step 1: Extract basic resume information
        print(f"[QUERY BUILDER] Step 1: Extracting basic resume info...")
        resume_info = extract_resume_info(resume)
        extracted_skills = resume_info.get("Skills", [])
        
        # Step 2: Identify skill domains and matching roles
        print(f"[QUERY BUILDER] Step 2: Analyzing skill domains and role matches...")
        domain_analysis = identify_skill_domains_and_roles(resume, extracted_skills)
        
        # Step 3: Combine user role with AI-suggested roles
        primary_roles = domain_analysis.get("primary_role_recommendations", [])
        secondary_roles = domain_analysis.get("secondary_role_options", [])
        
        # Create enhanced role list for search queries
        enhanced_roles = [role]  # Start with user-specified role
        enhanced_roles.extend(primary_roles[:3])  # Add top 3 AI-suggested primary roles
        enhanced_roles.extend(secondary_roles[:2])  # Add top 2 secondary roles
        
        # Remove duplicates while preserving order
        seen = set()
        unique_roles = []
        for r in enhanced_roles:
            if r and r.lower() not in seen:
                unique_roles.append(r)
                seen.add(r.lower())
        
        print(f"[QUERY BUILDER] Enhanced roles for search: {unique_roles}")

        # Enhanced salary handling
        salary = generate_salary_string(min_salary, salary_type) if min_salary else "Not specified"

        chain = prompt_template | llm | parser

        # Extract sample skills for template variables
        resume_words = resume.lower().split()
        common_skills = ["python", "javascript", "react", "node.js", "sql", "java", "css", "html"]
        found_skills = [skill for skill in extracted_skills if skill.lower() in resume.lower()]
        if not found_skills:
            found_skills = [skill for skill in common_skills if skill in resume.lower()]
        
        # Enhanced chain input with domain analysis
        chain_input = {
            "resume": resume,
            "role": role,
            "primary_role": unique_roles[0] if unique_roles else role,
            "alternative_role": unique_roles[1] if len(unique_roles) > 1 else f"{role} Developer",
            "role_variant": unique_roles[2] if len(unique_roles) > 2 else f"{role} Position",
            "location": location,
            "salary": salary,
            "salary_type": salary_type,
            "skill1": found_skills[0] if len(found_skills) > 0 else "Python",
            "skill2": found_skills[1] if len(found_skills) > 1 else "React", 
            "skill3": found_skills[2] if len(found_skills) > 2 else "SQL",
            "experience_keywords": "fresher entry-level graduate" if "intern" in role.lower() else "experienced professional",
            "format_instructions": parser.get_format_instructions(),
            "suggested_roles": unique_roles,  # Pass all suggested roles
            "primary_skills": extracted_skills[:5],  # Top 5 skills
            "domain_info": domain_analysis.get("skill_domain_summary", {})
        }

        result = chain.invoke(chain_input)

        # Post-process to ensure we have diverse queries
        if isinstance(result, dict) and "queries" in result:
            # Ensure we have different job boards represented
            job_boards = set()
            for query in result["queries"]:
                if isinstance(query, dict) and "job_board" in query:
                    job_boards.add(query["job_board"])
            
            # Add role-specific queries
            role_variants = result.get("role_variants", [])
            core_skills = result.get("skills", {}).get("core", [])
            
            role_specific = generate_role_specific_queries(role, role_variants, location, core_skills)
            result["queries"].extend(role_specific)
            
            # Add AI-suggested role queries without quotes
            for i, suggested_role in enumerate(unique_roles[1:4]):  # Use top 3 AI-suggested roles
                if suggested_role and suggested_role.lower() != role.lower():
                    ai_role_query = {
                        "query": f'site:{"naukri.com" if i % 2 == 0 else "indeed.com"} {suggested_role} {location}',
                        "type": "AI-Suggested Role",
                        "job_board": "naukri.com" if i % 2 == 0 else "indeed.com",
                        "focus": f"AI-identified role match: {suggested_role}",
                        "role_match": suggested_role,
                        "ai_suggested": True
                    }
                    result["queries"].append(ai_role_query)
            
            # Add fallback queries if we don't have enough diversity
            if len(job_boards) < 3:
                fallback_queries = generate_fallback_queries(role, location, core_skills)
                result["queries"].extend(fallback_queries)
            
            # Ensure we have intern-specific platform if role is intern
            if "intern" in role.lower():
                has_internshala = any("internshala" in q.get("job_board", "") for q in result["queries"])
                if not has_internshala:
                    result["queries"].append({
                        "query": f'site:internshala.com internship {location}',
                        "type": "Mandatory Intern Platform",
                        "job_board": "internshala.com",
                        "focus": "Essential internship platform coverage",
                        "role_match": "Generic internship",
                        "ai_suggested": False
                    })

        # Add domain analysis results to final output
        if isinstance(result, dict):
            result["domain_analysis"] = domain_analysis
            result["enhanced_roles"] = unique_roles
            result["skill_domains"] = domain_analysis.get("identified_domains", []) # Changed from "domains"
            result["resume_insights"] = {
                "extracted_skills": extracted_skills,
                "target_role": resume_info.get("Role", ""),
                "experience_level": resume_info.get("Experience", ""),
                "strongest_domain": domain_analysis.get("skill_domain_summary", {}).get("strongest_domain", ""),
                "ai_confidence": len(primary_roles) > 0  # Has AI suggested roles
            }

        print(f"[QUERY BUILDER] Generated {len(result.get('queries', []))} total queries with {len(unique_roles)} enhanced roles")
        return result if isinstance(result, dict) else {}

    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {str(e)}")
        return {}

# Step 6: Enhanced fallback query generator for better coverage
def generate_fallback_queries(role: str, location: str, core_skills: list) -> list:
    """Generate additional queries to ensure good coverage"""
    fallback_queries = []
    
    # Determine role category for targeted fallbacks
    role_lower = role.lower()
    
    if "intern" in role_lower:
        # Intern-specific fallbacks
        fallback_queries.append({
            "query": f'site:internshala.com "internship" {location}',
            "type": "Fallback - Intern Specific",
            "job_board": "internshala.com",
            "focus": "Internship-focused platform",
            "role_match": "Generic internship"
        })
        
        fallback_queries.append({
            "query": f'site:linkedin.com/jobs "summer intern" {location}',
            "type": "Fallback - Seasonal Intern",
            "job_board": "linkedin.com",
            "focus": "Seasonal internship opportunities",
            "role_match": "Summer internship"
        })
    
    elif any(term in role_lower for term in ["sde", "developer", "engineer"]):
        # Developer-specific fallbacks
        fallback_queries.append({
            "query": f'site:naukri.com "SDE" OR "Software Engineer" {location}',
            "type": "Fallback - SDE Focus",
            "job_board": "naukri.com",
            "focus": "SDE and Software Engineer roles",
            "role_match": "SDE/Software Engineer"
        })
        
        # Tech stack based query
        if core_skills:
            tech_stack = " OR ".join(core_skills[:3])
            fallback_queries.append({
                "query": f'site:wellfound.com ({tech_stack}) {location}',
                "type": "Fallback - Tech Stack",
                "job_board": "wellfound.com",
                "focus": "Startup-focused platform with tech stack",
                "role_match": "Tech stack based"
            })
    
    else:
        # Generic fallbacks for other roles
        fallback_queries.append({
            "query": f'site:wellfound.com "{role}" {location}',
            "type": "Fallback - Basic Role",
            "job_board": "wellfound.com",
            "focus": "Basic role search on startup platform",
            "role_match": "Original role"
        })
        
        # Skills-only query for indeed
        if core_skills:
            skills_query = " AND ".join(core_skills[:3])
            fallback_queries.append({
                "query": f'site:indeed.com {skills_query} {location}',
                "type": "Fallback - Skills Focus",
                "job_board": "indeed.com", 
                "focus": "Pure skills-based search",
                "role_match": "Skills-based match"
            })
    
    return fallback_queries

# Step 7: Role-specific query generator
def generate_role_specific_queries(role: str, role_variants: list, location: str, core_skills: list) -> list:
    """Generate additional role-specific queries based on role type"""
    specific_queries = []
    role_lower = role.lower()
    
    if "intern" in role_lower:
        # Add internship-specific queries
        specific_queries.extend([
            {
                "query": f'site:internshala.com "{role}" {location}',
                "type": "Internship Platform",
                "job_board": "internshala.com",
                "focus": "Dedicated internship platform",
                "role_match": "Primary internship role"
            },
            {
                "query": f'site:linkedin.com/jobs "graduate trainee" {location}',
                "type": "Graduate Program",
                "job_board": "linkedin.com",
                "focus": "Graduate trainee programs",
                "role_match": "Graduate trainee"
            }
        ])
    
    elif any(term in role_lower for term in ["data", "analyst", "scientist"]):
        # Data role specific queries
        if core_skills:
            data_skills = [skill for skill in core_skills if any(ds in skill.lower() for ds in ["python", "sql", "r", "tableau", "power bi", "excel"])]
            if data_skills:
                specific_queries.append({
                    "query": f'site:linkedin.com/jobs "data" AND {" AND ".join(data_skills[:2])} {location}',
                    "type": "Data Skills Focus",
                    "job_board": "linkedin.com",
                    "focus": "Data-specific skills combination",
                    "role_match": "Data role with skills"
                })
    
    return specific_queries


def analyze_resume_vs_job_description(resume_text: str, resume_info: dict, job_description: str) -> dict:
    """
    Comprehensive ATS analysis comparing resume against job description
    
    Args:
        resume_text: Raw resume text content
        resume_info: Parsed resume information (role, skills, experience)
        job_description: Job description text to analyze against
    
    Returns:
        dict: Detailed analysis including strengths, weaknesses, missing keywords, ATS score
    """
    try:
        # Create comprehensive ATS analysis prompt using the advanced evaluation framework
        ats_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced Applicant Tracking System (ATS) resume evaluator designed to simulate how modern hiring systems analyze and score resumes for relevance, quality, and presentation. Your job is to evaluate resumes and provide detailed assessment of their effectiveness based on industry best practices."""),
            ("human", """
**TASK**: Evaluate this resume against the provided job description for ATS compatibility and match quality.

**RESUME CONTENT:**
{resume_text}

**EXTRACTED RESUME INFO:**
- Role: {resume_role}
- Skills: {resume_skills}
- Experience Level: {experience_level}

**JOB DESCRIPTION:**
{job_description}

**EVALUATION CRITERIA:**

**Step 1: Job Description-Based Scoring (JD Provided)**

1. **Keyword Match (20% weight)**: Identify how well the resume incorporates keywords and phrases found in the job description, including tools, technologies, soft skills, and responsibilities.

2. **Skills Relevance (20% weight)**: Evaluate how the listed skills align with the required skills in the JD.

3. **Job Title Match (15% weight)**: Determine how closely the candidate's previous job titles match the desired role.

4. **Relevant Experience (15% weight)**: Assess whether the work experience demonstrates expertise in relevant areas, including total years of experience and recency.

5. **Education Fit (10% weight)**: Determine whether the degree(s), field of study, and institution level meet or exceed the minimum educational qualifications.

6. **Certifications (5% weight)**: Check if relevant industry certifications are present, particularly those mentioned in the JD.

7. **Section Completeness (5% weight)**: Ensure essential sections are present — Contact Info, Summary, Work Experience, Skills, Education, Projects, and Certifications.

8. **Resume Formatting (5% weight)**: Evaluate whether the resume is ATS-friendly — no tables, no multi-column layouts, minimal graphics, no header/footer content misuse.

9. **Grammar & Clarity (3% weight)**: Identify any spelling or grammatical issues and check for clarity and professionalism in language.

10. **Overall Presentation (2% weight)**: Consider layout readability, bullet point structure (action-oriented, achievement-focused), consistency in formatting, and effective use of space.

**SCORING METHODOLOGY:**
- **90-100%**: Excellent Fit - Resume closely matches most job requirements
- **75-89%**: Very Good Fit - Strong match with minor gaps
- **60-74%**: Good Fit - Decent match but needs improvement
- **40-59%**: Moderate Fit - Some alignment but significant gaps
- **20-39%**: Poor Fit - Limited alignment, major improvements needed
- **0-19%**: Not a Fit - Very little to no alignment

**CALCULATE SCORES DYNAMICALLY:**
- Count actual keyword matches vs total job keywords
- Assess skill overlap percentage
- Evaluate experience level alignment
- Consider industry/domain relevance
- Factor in role title similarity
- Weight each criterion appropriately

**RESPONSE FORMAT (JSON only):**
{{
    "overall_score": [CALCULATE_ACTUAL_SCORE_0_TO_100],
    "match_percentage": [SAME_AS_OVERALL_SCORE],
    "fit_level": "[excellent_fit|very_good_fit|good_fit|moderate_fit|poor_fit|not_a_fit]",
    "strengths": [
        "List specific strengths found in resume that align with job requirements",
        "Be specific about what matches well and why"
    ],
    "weaknesses": [
        "List specific gaps and mismatches found",
        "Be specific about what's missing or inadequate"
    ],
    "missing_keywords": [
        "List critical keywords from job description not found in resume"
    ],
    "missing_skills": [
        "List required/preferred skills mentioned in job but not in resume"
    ],
    "ats_optimization": [
        "Provide specific, actionable optimization tips for ATS scanning",
        "Focus on formatting, keyword placement, and structure improvements"
    ],
    "keyword_analysis": {{
        "total_job_keywords": [COUNT_ACTUAL_KEYWORDS_IN_JOB],
        "matched_keywords": [COUNT_ACTUAL_MATCHES_IN_RESUME],
        "keyword_match_rate": [CALCULATE_PERCENTAGE],
        "critical_missing": ["List most important missing keywords"],
        "well_matched": ["List keywords found in both"]
    }},
    "experience_alignment": {{
        "required_experience": "[Extract from job description]",
        "candidate_experience": "[Extract from resume]",
        "alignment_score": [CALCULATE_0_TO_100],
        "notes": "Detailed assessment of experience match"
    }},
    "action_items": [
        "List specific, actionable items based on actual analysis",
        "Focus on the most impactful changes for this specific job"
    ],
    "category_breakdown": {{
        "keyword_match": [CALCULATE_0_TO_100],
        "skills_relevance": [CALCULATE_0_TO_100],
        "job_title_match": [CALCULATE_0_TO_100],
        "experience_alignment": [CALCULATE_0_TO_100],
        "education_fit": [CALCULATE_0_TO_100],
        "certifications": [CALCULATE_0_TO_100],
        "section_completeness": [CALCULATE_0_TO_100],
        "resume_formatting": [CALCULATE_0_TO_100],
        "grammar_clarity": [CALCULATE_0_TO_100],
        "overall_presentation": [CALCULATE_0_TO_100]
    }},
    "recommendations": {{
        "high_priority": [
            "Most critical improvements based on actual gaps found"
        ],
        "medium_priority": [
            "Important but secondary improvements"
        ],
        "low_priority": [
            "Nice-to-have improvements"
        ]
    }},
    "evaluation_summary": "Brief summary of the overall assessment and key findings"
}}

**IMPORTANT SCORING RULES**: 
- **NEVER use example scores (like 78, 85, etc.) - calculate actual scores based on analysis**
- **Count exact keyword matches** - if job mentions "Python" and resume has "Python", count it
- **Be honest about gaps** - if major skills are missing, score should be lower
- **Vary scores significantly** - different resumes should get very different scores
- **Focus on role relevance** - wrong role type should get low scores
- **Consider experience mismatch** - junior vs senior misalignment affects score
- **Weight criteria appropriately** - keyword match and skills relevance are most important
- Respond with ONLY the JSON, no other text""")
        ])
        
        # Create analysis chain
        analysis_chain = ats_analysis_prompt | llm | parser
        
        # Format skills for display
        skills_text = ", ".join(resume_info.get("Skills", [])) if resume_info.get("Skills") else "None extracted"
        
        # Perform analysis
        print(f"[ATS ANALYSIS] Starting comprehensive analysis...")
        analysis_result = analysis_chain.invoke({
            "resume_text": resume_text,
            "resume_role": resume_info.get("Role", "Not specified"),
            "resume_skills": skills_text,
            "experience_level": resume_info.get("Experience", "Not specified"),
            "job_description": job_description
        })
        
        # Add metadata
        analysis_result["analysis_metadata"] = {
            "analyzed_at": str(datetime.now()),
            "resume_length": len(resume_text),
            "job_description_length": len(job_description),
            "resume_role": resume_info.get("Role", ""),
            "skills_count": len(resume_info.get("Skills", [])),
            "analysis_type": "job_description_based"
        }
        
        print(f"[ATS ANALYSIS] Completed with score: {analysis_result.get('overall_score', 'N/A')}")
        
        return analysis_result
        
    except Exception as e:
        print(f"[ATS ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
        # Return error structure
        return {
            "overall_score": 0,
            "match_percentage": 0,
            "strengths": [],
            "weaknesses": [f"Analysis failed: {str(e)}"],
            "missing_keywords": [],
            "missing_skills": [],
            "ats_optimization": ["Unable to complete analysis due to technical error"],
            "keyword_analysis": {
                "total_job_keywords": 0,
                "matched_keywords": 0,
                "keyword_match_rate": 0,
                "critical_missing": [],
                "well_matched": []
            },
            "experience_alignment": {
                "alignment_score": 0,
                "notes": "Analysis unavailable"
            },
            "action_items": ["Please try again or contact support"],
            "error": True,
            "error_message": str(e)
        }

def analyze_resume_standalone(resume_text: str, resume_info: dict) -> dict:
    """
    Comprehensive ATS analysis of resume against general best practices (no job description)
    
    Args:
        resume_text: Raw resume text content
        resume_info: Parsed resume information (role, skills, experience)
    
    Returns:
        dict: Detailed analysis including strengths, weaknesses, ATS score
    """
    try:
        # Initialize LLM and parser
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            max_tokens=8000,
            google_api_key=GEMINI_API_KEY
        )
        parser = JsonOutputParser()
        
        # Create comprehensive standalone ATS analysis prompt
        standalone_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced Applicant Tracking System (ATS) resume evaluator designed to simulate how modern hiring systems analyze and score resumes for relevance, quality, and presentation. Your job is to evaluate resumes and provide detailed assessment of their effectiveness based on industry best practices."""),
            ("human", """
**TASK**: Evaluate this resume based on best practices and general expectations for strong resumes in technical and professional roles.

**RESUME CONTENT:**
{resume_text}

**EXTRACTED RESUME INFO:**
- Role: {resume_role}
- Skills: {resume_skills}
- Experience Level: {experience_level}

**EVALUATION CRITERIA:**

**Step 2: General Best Practices Evaluation (No JD Provided)**

1. **ATS-Friendliness (25% weight)**: Ensure formatting avoids tables, columns, images, or other elements that might confuse parsing systems. Check for clean, parseable text structure.

2. **Section Completeness (20% weight)**: Check for presence of all important sections — Contact Info, Summary, Work Experience, Education, Skills, and optional Projects/Certifications.

3. **Grammar & Language (15% weight)**: Look for correct grammar, sentence structure, and use of professional language. Identify any spelling or grammatical issues.

4. **Resume Length (10% weight)**: One page is ideal for entry-level candidates; 1–2 pages is acceptable for experienced professionals. Penalize unnecessarily long resumes.

5. **Bullet Point Quality (10% weight)**: Assess whether bullet points begin with action verbs and communicate accomplishments clearly, ideally with measurable results.

6. **Keyword Strength (10% weight)**: Look for presence of commonly expected tools, languages, and frameworks for the field (e.g., Python, Git, APIs, Agile, etc.).

7. **Work Experience Quality (5% weight)**: Ensure that experience descriptions are relevant and well-written, with clear roles and responsibilities.

8. **Timeline Consistency (3% weight)**: Ensure dates are chronologically sound, complete, and formatted uniformly.

9. **Soft Skills Indicators (2% weight)**: Note presence of leadership, communication, teamwork, and problem-solving where applicable.

10. **Design and Layout (2% weight)**: Ensure clean alignment, proper font size, spacing, and visual hierarchy.

**SCORING METHODOLOGY:**
- **90-100%**: Excellent Resume - Follows all best practices, highly ATS-friendly
- **75-89%**: Very Good Resume - Strong adherence to best practices with minor issues
- **60-74%**: Good Resume - Decent quality but needs some improvements
- **40-59%**: Fair Resume - Some good elements but significant improvements needed
- **20-39%**: Poor Resume - Major issues with formatting, content, or structure
- **0-19%**: Very Poor Resume - Serious problems that need immediate attention

**CALCULATE SCORES DYNAMICALLY:**
- Assess ATS compatibility based on formatting and structure
- Count essential sections present vs required
- Evaluate grammar and language quality
- Check resume length appropriateness
- Assess bullet point effectiveness
- Count relevant keywords for the field
- Review experience description quality
- Verify timeline consistency
- Identify soft skills presence
- Evaluate overall design and layout

**RESPONSE FORMAT (JSON only):**
{{
    "overall_score": [CALCULATE_ACTUAL_SCORE_0_TO_100],
    "ats_compatibility_score": [CALCULATE_0_TO_100],
    "fit_level": "[excellent|very_good|good|fair|poor|very_poor]",
    "strengths": [
        "List specific strengths found in the resume",
        "Be specific about what works well and why"
    ],
    "weaknesses": [
        "List specific areas that need improvement",
        "Be specific about what's missing or inadequate"
    ],
    "ats_optimization": [
        "Provide specific, actionable optimization tips for ATS scanning",
        "Focus on formatting, structure, and keyword improvements"
    ],
    "section_analysis": {{
        "contact_info": "[present|missing|incomplete]",
        "summary": "[present|missing|incomplete]",
        "work_experience": "[present|missing|incomplete]",
        "education": "[present|missing|incomplete]",
        "skills": "[present|missing|incomplete]",
        "projects": "[present|missing|incomplete]",
        "certifications": "[present|missing|incomplete]"
    }},

    "content_analysis": {{
        "grammar_quality": [CALCULATE_0_TO_100],
        "bullet_point_quality": [CALCULATE_0_TO_100],
        "keyword_density": [CALCULATE_0_TO_100],
        "experience_quality": [CALCULATE_0_TO_100],
        "timeline_consistency": [CALCULATE_0_TO_100],
        "soft_skills_presence": [CALCULATE_0_TO_100]
    }},
    "action_items": [
        "List specific, actionable items to improve the resume",
        "Focus on the most impactful changes for general ATS compatibility"
    ],
    "category_breakdown": {{
        "ats_friendliness": [CALCULATE_0_TO_100],
        "section_completeness": [CALCULATE_0_TO_100],
        "grammar_language": [CALCULATE_0_TO_100],
        "resume_length": [CALCULATE_0_TO_100],
        "bullet_point_quality": [CALCULATE_0_TO_100],
        "keyword_strength": [CALCULATE_0_TO_100],
        "work_experience_quality": [CALCULATE_0_TO_100],
        "timeline_consistency": [CALCULATE_0_TO_100],
        "soft_skills_indicators": [CALCULATE_0_TO_100],
        "design_layout": [CALCULATE_0_TO_100]
    }},
    "recommendations": {{
        "high_priority": [
            "Most critical improvements for ATS compatibility"
        ],
        "medium_priority": [
            "Important improvements for overall quality"
        ],
        "low_priority": [
            "Nice-to-have improvements"
        ]
    }},
    "evaluation_summary": "Brief summary of the overall assessment and key findings"
}}

**IMPORTANT SCORING RULES**: 
- **NEVER use example scores (like 78, 85, etc.) - calculate actual scores based on analysis**
- **Focus on ATS compatibility** - this is the most important factor for standalone evaluation
- **Be honest about issues** - if there are major formatting problems, score should be lower
- **Vary scores significantly** - different resumes should get very different scores
- **Weight criteria appropriately** - ATS-friendliness and section completeness are most important
- **Consider industry standards** - evaluate against expectations for the candidate's field
- Respond with ONLY the JSON, no other text""")
        ])
        
        # Create analysis chain
        analysis_chain = standalone_analysis_prompt | llm | parser
        
        # Format skills for display
        skills_text = ", ".join(resume_info.get("Skills", [])) if resume_info.get("Skills") else "None extracted"
        
        # Perform analysis
        print(f"[STANDALONE ATS ANALYSIS] Starting comprehensive analysis...")
        analysis_result = analysis_chain.invoke({
            "resume_text": resume_text,
            "resume_role": resume_info.get("Role", "Not specified"),
            "resume_skills": skills_text,
            "experience_level": resume_info.get("Experience", "Not specified")
        })
        
        # Add metadata
        analysis_result["analysis_metadata"] = {
            "analyzed_at": str(datetime.now()),
            "resume_length": len(resume_text),
            "resume_role": resume_info.get("Role", ""),
            "skills_count": len(resume_info.get("Skills", [])),
            "analysis_type": "standalone_ats"
        }
        
        print(f"[STANDALONE ATS ANALYSIS] Completed with score: {analysis_result.get('overall_score', 'N/A')}")
        
        return analysis_result
        
    except Exception as e:
        print(f"[STANDALONE ATS ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
        # Return error structure
        return {
            "overall_score": 0,
            "ats_compatibility_score": 0,
            "strengths": [],
            "weaknesses": [f"Analysis failed: {str(e)}"],
            "ats_optimization": ["Unable to complete analysis due to technical error"],
            "section_analysis": {
                "contact_info": "unknown",
                "summary": "unknown",
                "work_experience": "unknown",
                "education": "unknown",
                "skills": "unknown",
                "projects": "unknown",
                "certifications": "unknown"
            },
            "formatting_analysis": {
                "ats_friendly": False,
                "uses_tables": False,
                "uses_columns": False,
                "has_images": False,
                "clean_structure": False,
                "proper_spacing": False
            },
            "content_analysis": {
                "grammar_quality": 0,
                "bullet_point_quality": 0,
                "keyword_density": 0,
                "experience_quality": 0,
                "timeline_consistency": 0,
                "soft_skills_presence": 0
            },
            "action_items": ["Please try again or contact support"],
            "error": True,
            "error_message": str(e)
        }