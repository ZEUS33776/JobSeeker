from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import GEMINI_API_KEY
import google.generativeai as genai
from datetime import datetime

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
                "domains": [],
                "suggested_roles": [],
                "role_mapping": {}
            }
        
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

Respond with ONLY the JSON, no other text.
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
        
        return {
            "domains": domain_result.get("identified_domains", []),
            "suggested_roles": domain_result.get("suggested_roles", []),
            "primary_roles": primary_roles,
            "secondary_roles": secondary_roles,
            "skill_summary": domain_result.get("skill_domain_summary", {}),
            "role_mapping": domain_result
        }
        
    except Exception as e:
        print(f"[DOMAIN ANALYSIS ERROR] {type(e).__name__}: {str(e)}")
        return {
            "domains": [],
            "suggested_roles": [],
            "primary_roles": [],
            "secondary_roles": [],
            "skill_summary": {},
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
        
        return {
            "Role": target_role,
            "Skills": skills,
            "Experience": experience_level
        }
        
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
        primary_roles = domain_analysis.get("primary_roles", [])
        secondary_roles = domain_analysis.get("secondary_roles", [])
        
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
            "domain_info": domain_analysis.get("skill_summary", {})
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
            result["skill_domains"] = domain_analysis.get("domains", [])
            result["resume_insights"] = {
                "extracted_skills": extracted_skills,
                "target_role": resume_info.get("Role", ""),
                "experience_level": resume_info.get("Experience", ""),
                "strongest_domain": domain_analysis.get("skill_summary", {}).get("strongest_domain", ""),
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
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        # Initialize LLM and parser
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            max_tokens=8000,
            google_api_key=GEMINI_API_KEY
        )
        parser = JsonOutputParser()
        
        # Create comprehensive ATS analysis prompt
        ats_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert ATS (Applicant Tracking System) consultant and resume optimization specialist. 
            Your job is to provide comprehensive analysis comparing a resume against a specific job description, 
            focusing on ATS compatibility, keyword matching, and optimization recommendations."""),
            ("human", """
**TASK**: Analyze this resume against the provided job description for ATS compatibility and match quality.

**RESUME CONTENT:**
{resume_text}

**EXTRACTED RESUME INFO:**
- Role: {resume_role}
- Skills: {resume_skills}
- Experience Level: {experience_level}

**JOB DESCRIPTION:**
{job_description}

**ANALYSIS REQUIREMENTS:**

Perform a comprehensive ATS analysis and provide detailed insights in the following areas:

1. **OVERALL MATCH SCORE** (0-100): Calculate based on keyword alignment, skill match, experience relevance
2. **STRENGTHS**: What aspects of the resume align well with the job requirements
3. **WEAKNESSES**: Areas where the resume falls short or lacks relevance
4. **MISSING KEYWORDS**: Critical keywords from job description not found in resume
5. **MISSING SKILLS**: Required/preferred skills mentioned in job but not in resume
6. **ATS OPTIMIZATION**: Specific recommendations to improve ATS scanning
7. **KEYWORD DENSITY**: Analysis of how well resume matches job keywords
8. **EXPERIENCE ALIGNMENT**: How well experience level and background match requirements
9. **ACTION ITEMS**: Specific steps to improve the resume for this position

**ANALYSIS CRITERIA:**
- Focus on exact keyword matches (case-insensitive)
- Consider synonyms and related terms
- Evaluate technical skills, soft skills, tools, and technologies
- Assess experience level alignment
- Check for industry-specific terminology
- Consider required vs preferred qualifications

**SCORING GUIDELINES:**
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

**RESPONSE FORMAT (JSON only):**
{{
    "overall_score": [CALCULATE_ACTUAL_SCORE_0_TO_100],
    "match_percentage": [SAME_AS_OVERALL_SCORE],
    "fit_level": "[excellent_fit|very_good_fit|good_fit|moderate_fit|poor_fit|not_a_fit]",
    "strengths": [
        "List actual strengths found in resume that match job",
        "Be specific about what aligns well"
    ],
    "weaknesses": [
        "List actual gaps and mismatches found",
        "Be specific about what's missing"
    ],
    "missing_keywords": [
        "List actual keywords from job not found in resume"
    ],
    "missing_skills": [
        "List actual skills mentioned in job but not in resume"
    ],
    "ats_optimization": [
        "Provide specific, actionable optimization tips",
        "Based on actual analysis of resume vs job"
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
        "notes": "Actual assessment of experience match"
    }},
    "action_items": [
        "List specific, actionable items based on actual analysis",
        "Focus on the most impactful changes for this specific job"
    ],
    "category_breakdown": {{
        "technical_skills": [CALCULATE_0_TO_100],
        "soft_skills": [CALCULATE_0_TO_100],
        "experience_level": [CALCULATE_0_TO_100],
        "education_requirements": [CALCULATE_0_TO_100],
        "industry_knowledge": [CALCULATE_0_TO_100]
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
    }}
}}

**IMPORTANT SCORING RULES**: 
- **NEVER use example scores (like 78, 85, etc.) - calculate actual scores**
- **Count exact keyword matches** - if job mentions "Python" and resume has "Python", count it
- **Be honest about gaps** - if major skills are missing, score should be lower
- **Vary scores significantly** - different resumes should get very different scores
- **Focus on role relevance** - wrong role type should get low scores
- **Consider experience mismatch** - junior vs senior misalignment affects score
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
            "skills_count": len(resume_info.get("Skills", []))
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