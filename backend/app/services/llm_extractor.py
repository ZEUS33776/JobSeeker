# app/services/llm_extractor.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import GEMINI_API_KEY
import google.generativeai as genai

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

# Step 3: Refined Prompt Template (short queries, limited keywords)
try:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a job search optimization expert."),
        ("human", """
You are a job search optimization assistant.

A user has uploaded their resume and wants to find job openings related to the role: **\"{role}\"**.

---
**Your Tasks:**

1. Extract **5–7 most relevant technical skills** from the resume. Focus only on job-relevant tools, libraries, and programming languages.

2. Generate **3–5 short, well-formed Google search queries** to help them find relevant job listings.

---
**Query Rules:**

- Use one site per query:
  - site:linkedin.com/jobs
  - site:wellfound.com/jobs
  - site:naukri.com

- Enclose all **role variants** in quotes and connect with OR:
  Example:
  ("Backend Intern" OR "Software Engineering Intern")

- Add 5–7 extracted skills after the role variants (unquoted):
  Example:
  python fastapi langchain node.js postgresql

- Append **location** and optionally **salary** at the end:
  Bengaluru ₹30000 ₹40000 ₹50000

- **Each query must be under 25 words**

---
{format_instructions}

Return ONLY valid JSON like:
```json
{{
  "role": "...",
  "role_variants": [...],
  "skills": [...],
  "queries": [...]
}}
```

Resume:
{resume}

Location: {location}  
Salary: {salary}
""")
    ])
except Exception as e:
    raise

# Step 4: Salary string generator
def generate_salary_string(min_salary: int, salary_type: str = "monthly") -> str:
    try:
        if not isinstance(min_salary, int) or min_salary <= 0:
            return ""
        if salary_type == "monthly":
            return " ".join([f"₹{min_salary + i * 10000}" for i in range(3)])
        else:
            return " ".join([f'\"{min_salary + i} LPA\"' for i in range(3)])
    except Exception:
        return ""

# Step 5: Core function to extract LLM-based info
def extract_keywords_from_llm(resume: str, role: str, min_salary: int = None, location: str = "Bengaluru", salary_type: str = "monthly") -> dict:
    try:
        if not resume or not isinstance(resume, str):
            return {}
        if not location or not isinstance(location, str):
            location = "Bengaluru"

        salary = generate_salary_string(min_salary, salary_type) if min_salary else ""

        chain = prompt_template | llm | parser

        chain_input = {
            "resume": resume,
            "role": role,
            "location": location,
            "salary": salary or "Not specified",
            "salary_type": salary_type,
            "format_instructions": parser.get_format_instructions()
        }

        result = chain.invoke(chain_input)

        return result if isinstance(result, dict) else {}

    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {str(e)}")
        return {}
