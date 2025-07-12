# JobSeeker – AI-Powered Job Search Platform

## 🚀 Overview
JobSeeker is a one-stop intelligent job search platform that takes a user's resume and streamlines the entire application pipeline:

- 🧠 Extracts relevant skills and roles from the resume using LLMs
- 🔍 Generates targeted search queries and fetches job listings from platforms like LinkedIn, Naukri, and Wellfound
- 📊 Scores the resume against job descriptions (1–100 scale)
- ✍️ Suggests improvements and regenerates a tailored resume using LaTeX
- 📄 Outputs a downloadable PDF optimized for ATS

Built with modular architecture for scalability and fast iteration.

---

## 💡 Key Features

- **Resume Parsing**: Extracts structured information and skills from any resume PDF
- **LLM-Driven Query Generation**: Dynamically creates 5–7 Google search queries for job platforms
- **Job Search**: Scrapes and filters 10–20 job postings with salary, location, and skill match
- **Resume Scoring**: Matches user resume with job descriptions using a contextual multi-agent RAG system
- **LaTeX Resume Generation**: Converts content into professional, ATS-optimized format using Jake's template
- **Live Feedback**: Suggests actionable improvements for each job
- **Multi-Agent AI Pipeline**: LangGraph + CrewAI agents handle scoring, matching, and suggestion workflows

---

## 🧱 Tech Stack

| Layer         | Tools / Frameworks                                             |
|--------------|-----------------------------------------------------------------|
| Frontend     | React.js (JavaScript), Tailwind CSS                             |
| Backend      | FastAPI (Python), LangChain, LlamaIndex, CrewAI, LangGraph     |
| AI/LLM       | Gemini Pro (Google AI Studio), LangChain, Custom Prompts       |
| PDF / Latex  | PyMuPDF, LaTeX, pdfLaTeX                                        |
| Infra        | Docker, GCP (Cloud Run/Compute), Supabase                      |
| Others       | Firecrawl (scraping), Serper.dev/Bing Search API               |

---

## 📂 Project Structure

```
jobseeker-backend/
├── app/
│   ├── main.py                  # FastAPI app entry
│   ├── api/                     # Route handlers
│   │   └── routes.py
│   ├── services/                # Core logic: LLMs, query, parsing, search
│   │   ├── llm_extractor.py
│   │   ├── query_builder.py
│   │   ├── search_engine.py
│   │   ├── parser.py
│   │   └── resume_ingestor.py
│   ├── models/                  # Pydantic schemas
│   │   └── job.py
│   ├── core/                    # Config, logging, environment
│   │   ├── config.py
│   │   └── logger.py
│   └── cache/                   # (Optional) Redis caching
├── scripts/                     # Seeders, utilities
├── tests/                       # Pytest-based tests
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. **Upload Resume** (PDF)
2. **Extract Content** using `PyMuPDF`
3. **LLM Generates**:
    - Roles & Role Variants
    - 5–7 Skills
    - 3–5 Google Search Queries
4. **Job Search Engine** scrapes using Firecrawl or SERP API
5. **RAG Pipeline** (LangGraph + CrewAI):
    - Fetches job description
    - Scores user's resume
    - Suggests improvements
6. **Resume Modifier** rewrites sections using LLM
7. **Latex Generator** rebuilds new resume and returns PDF

---

## 🔐 Environment Variables

```env
GEMINI_API_KEY=your_google_genai_api_key
SERPER_API_KEY=your_serper_or_bing_api_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

---

## 🧪 Testing

Run unit tests:
```bash
pytest tests/
```

---

## 🛠 Setup (Local)

```bash
git clone https://github.com/yourname/jobseeker.git
cd jobseeker
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📦 Docker

```bash
docker build -t jobseeker .
docker run -p 8000:8000 jobseeker
```

---

## 📌 Roadmap

- [x] Resume Parsing & Role Extraction
- [x] Query Generation with LangChain
- [x] Job Search Engine (Firecrawl/Serper)
- [x] Resume Scoring via LLM
- [x] LaTeX PDF Generation
- [ ] User Authentication & Session Saving
- [ ] Job Application Tracker
- [ ] Smart Email Notifier (optional)

---

## 👨‍💻 Author
**Arjun Deshmukh**  


---

## 📜 License
MIT License — feel free to fork, contribute, and build upon it.

---

> "Designed to save time, optimize resumes, and increase job match accuracy using AI."

---
