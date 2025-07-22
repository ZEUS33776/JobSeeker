"""
Resume Builder Service
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import re

from app.models.resume_builder import (
    ResumeTemplate, ResumeData, LLMResumeResponse, 
    PDFGenerationRequest, PDFGenerationResponse
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from app.core.config import GEMINI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

class ResumeBuilderService:
    """Service for resume building and template management"""
    
    def __init__(self):
        self.templates_dir = Path("Resume_template_latex")
        self.images_dir = Path("Resume_template_images")
        self.templates_cache = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load available templates from the templates directory"""
        try:
            self.templates_cache = {}
            
            # Scan for .tex files in the LaTeX templates directory
            if self.templates_dir.exists():
                for tex_file in self.templates_dir.glob("*.tex"):
                    template_id = tex_file.stem  # filename without extension
                    
                    # Check if corresponding image exists
                    image_extensions = ['.png', '.jpg', '.jpeg']
                    image_file = None
                    for ext in image_extensions:
                        potential_image = self.images_dir / f"{template_id}{ext}"
                        if potential_image.exists():
                            image_file = potential_image
                            break
                    
                    # Create template entry
                    template_data = {
                        "id": template_id,
                        "name": self._format_template_name(template_id),
                        "description": self._get_template_description(template_id),
                        "image_url": f"/api/resume-builder/templates/{template_id}/image",
                        "latex_file": tex_file.name,
                        "category": self._get_template_category(template_id),
                        "tags": self._get_template_tags(template_id)
                    }
                    
                    self.templates_cache[template_id] = template_data
            
            # If no templates found, fall back to hardcoded ones
            if not self.templates_cache:
                logger.warning("No template files found, using fallback templates")
                self.templates_cache = {
                    "jakes_resume": {
                        "id": "jakes_resume",
                        "name": "Jake's Resume",
                        "description": "Clean, modern template with professional styling",
                        "image_url": "/api/resume-builder/templates/jakes_resume/image",
                        "latex_file": "jakes_resume.tex",
                        "category": "Modern",
                        "tags": ["clean", "professional", "tech"]
                    },
                    "deedy_resume": {
                        "id": "deedy_resume", 
                        "name": "Deedy's Resume",
                        "description": "Classic academic-style resume with detailed sections",
                        "image_url": "/api/resume-builder/templates/deedy_resume/image",
                        "latex_file": "deedy_resume.tex",
                        "category": "Classic",
                        "tags": ["academic", "detailed", "traditional"]
                    },
                    "modern_tech": {
                        "id": "modern_tech",
                        "name": "Modern Tech Resume",
                        "description": "Contemporary design optimized for tech professionals",
                        "image_url": "/api/resume-builder/templates/modern_tech/image",
                        "latex_file": "modern_tech.tex",
                        "category": "Tech",
                        "tags": ["modern", "tech", "minimal"]
                    }
                }
            
            logger.info(f"Loaded {len(self.templates_cache)} resume templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self.templates_cache = {}
    
    def _format_template_name(self, template_id: str) -> str:
        """Format template ID into a readable name"""
        return template_id.replace('_', ' ').title()
    
    def _get_template_description(self, template_id: str) -> str:
        """Get description for a template"""
        descriptions = {
            "jakes_resume": "Clean, modern template with professional styling",
            "deedy_resume": "Classic academic-style resume with detailed sections", 
            "modern_tech": "Contemporary design optimized for tech professionals"
        }
        return descriptions.get(template_id, "Professional resume template")
    
    def _get_template_category(self, template_id: str) -> str:
        """Get category for a template"""
        categories = {
            "jakes_resume": "Modern",
            "deedy_resume": "Classic",
            "modern_tech": "Tech"
        }
        return categories.get(template_id, "General")
    
    def _get_template_tags(self, template_id: str) -> List[str]:
        """Get tags for a template"""
        tags = {
            "jakes_resume": ["clean", "professional", "tech"],
            "deedy_resume": ["academic", "detailed", "traditional"],
            "modern_tech": ["modern", "tech", "minimal"]
        }
        return tags.get(template_id, ["professional"])
    
    def get_templates(self) -> List[ResumeTemplate]:
        """Get list of available templates"""
        templates = []
        for template_id, template_data in self.templates_cache.items():
            templates.append(ResumeTemplate(**template_data))
        return templates
    
    def get_template(self, template_id: str) -> Optional[ResumeTemplate]:
        """Get specific template by ID"""
        if template_id in self.templates_cache:
            return ResumeTemplate(**self.templates_cache[template_id])
        return None
    
    def get_template_latex(self, template_id: str) -> Optional[str]:
        """Get LaTeX code for a specific template"""
        try:
            template = self.get_template(template_id)
            if not template:
                return None
            
            # Try to load from file first
            tex_file = self.templates_dir / template.latex_file
            if tex_file.exists():
                with open(tex_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Fall back to hardcoded templates if file doesn't exist
            logger.warning(f"Template file {tex_file} not found, using fallback")
            latex_templates = {
                "jakes_resume": self._get_jakes_latex_template(),
                "deedy_resume": self._get_deedy_latex_template(),
                "modern_tech": self._get_modern_tech_latex_template()
            }
            
            return latex_templates.get(template_id)
        except Exception as e:
            logger.error(f"Error loading template LaTeX: {e}")
            return None
    
    def _get_jakes_latex_template(self) -> str:
        """Get Jake's Resume LaTeX template"""
        return r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\usepackage{graphicx}
\usepackage{fontspec}
\usepackage{xcolor}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries\color{black}
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is readable by copying the fonts to a Mac directory
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}
}

\newcommand{\resumeEducationHeading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeOrganizationHeading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSkillHeading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING----------
% \begin{center}
%     \textbf{\Huge \scshape Name} \\ \vspace{3pt}
%     \small
%     \faIcon{phone} phone-number $|$ 
%     \faIcon{envelope} \href{mailto:email@email.com}{email@email.com} $|$ 
%     \faIcon{map-marker-alt} location $|$ 
%     \faIcon{github} \href{https://github.com/username}{github.com/username} $|$
%     \faIcon{linkedin} \href{https://linkedin.com/in/username}{linkedin.com/in/username}
% \end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeEducationHeading
      {University Name}{Expected Graduation Date}
      {Degree Name}{GPA: X.XX}
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Company Name}{Location}
      {Job Title}{Start Date - End Date}
      \resumeItemListStart
        \item Achievement 1
        \item Achievement 2
        \item Achievement 3
      \resumeItemListEnd
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
        {\href{https://project-url.com}{Project Name}}{Technologies Used}
        \resumeItemListStart
          \item Project description and achievements
          \item Key features implemented
          \item Technologies and tools used
        \resumeItemListEnd
    \resumeSubHeadingListEnd

%-----------SKILLS-----------
\section{Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{Languages:} Language1, Language2, Language3 \\
    \textbf{Technologies:} Technology1, Technology2, Technology3 \\
    \textbf{Tools:} Tool1, Tool2, Tool3
    }}
 \end{itemize}

\end{document}
"""
    
    def _get_deedy_latex_template(self) -> str:
        """Get Deedy's Resume LaTeX template"""
        return r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\usepackage{graphicx}
\usepackage{fontspec}
\usepackage{xcolor}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries\color{black}
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}
}

\newcommand{\resumeEducationHeading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Huge \scshape Name} \\ \vspace{3pt}
    \small
    \faIcon{phone} phone-number $|$ 
    \faIcon{envelope} \href{mailto:email@email.com}{email@email.com} $|$ 
    \faIcon{map-marker-alt} location $|$ 
    \faIcon{github} \href{https://github.com/username}{github.com/username} $|$
    \faIcon{linkedin} \href{https://linkedin.com/in/username}{linkedin.com/in/username}
\end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeEducationHeading
      {University Name}{Expected Graduation Date}
      {Degree Name}{GPA: X.XX}
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Company Name}{Location}
      {Job Title}{Start Date - End Date}
      \resumeItemListStart
        \item Achievement 1
        \item Achievement 2
        \item Achievement 3
      \resumeItemListEnd
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
        {\href{https://project-url.com}{Project Name}}{Technologies Used}
        \resumeItemListStart
          \item Project description and achievements
          \item Key features implemented
          \item Technologies and tools used
        \resumeItemListEnd
    \resumeSubHeadingListEnd

%-----------SKILLS-----------
\section{Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{Languages:} Language1, Language2, Language3 \\
    \textbf{Technologies:} Technology1, Technology2, Technology3 \\
    \textbf{Tools:} Tool1, Tool2, Tool3
    }}
 \end{itemize}

\end{document}
"""
    
    def _get_modern_tech_latex_template(self) -> str:
        """Get Modern Tech Resume LaTeX template"""
        return r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\usepackage{graphicx}
\usepackage{fontspec}
\usepackage{xcolor}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries\color{black}
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}
}

\newcommand{\resumeEducationHeading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Huge \scshape Name} \\ \vspace{3pt}
    \small
    \faIcon{phone} phone-number $|$ 
    \faIcon{envelope} \href{mailto:email@email.com}{email@email.com} $|$ 
    \faIcon{map-marker-alt} location $|$ 
    \faIcon{github} \href{https://github.com/username}{github.com/username} $|$
    \faIcon{linkedin} \href{https://linkedin.com/in/username}{linkedin.com/in/username}
\end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeEducationHeading
      {University Name}{Expected Graduation Date}
      {Degree Name}{GPA: X.XX}
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Company Name}{Location}
      {Job Title}{Start Date - End Date}
      \resumeItemListStart
        \item Achievement 1
        \item Achievement 2
        \item Achievement 3
      \resumeItemListEnd
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
        {\href{https://project-url.com}{Project Name}}{Technologies Used}
        \resumeItemListStart
          \item Project description and achievements
          \item Key features implemented
          \item Technologies and tools used
        \resumeItemListEnd
    \resumeSubHeadingListEnd

%-----------SKILLS-----------
\section{Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{Languages:} Language1, Language2, Language3 \\
    \textbf{Technologies:} Technology1, Technology2, Technology3 \\
    \textbf{Tools:} Tool1, Tool2, Tool3
    }}
 \end{itemize}

\end{document}
"""
    
    def generate_resume_latex(self, template_id: str, resume_data: ResumeData, user_text: str = "") -> Optional[LLMResumeResponse]:
        """Generate LaTeX resume using LLM"""
        try:
            logger.info(f"[generate_resume_latex] Start for template_id={template_id}")
            print(f"[generate_resume_latex] Start for template_id={template_id}")
            # Get template LaTeX code
            template_latex = self.get_template_latex(template_id)
            logger.info(f"[generate_resume_latex] Got template LaTeX for {template_id}")
            print(f"[generate_resume_latex] Got template LaTeX for {template_id}")
            if not template_latex:
                logger.error(f"Template LaTeX not found for {template_id}")
                print(f"Template LaTeX not found for {template_id}")
                return None
            
            template = self.get_template(template_id)
            logger.info(f"[generate_resume_latex] Got template object for {template_id}")
            print(f"[generate_resume_latex] Got template object for {template_id}")
            if not template:
                logger.error(f"Template not found for {template_id}")
                print(f"Template not found for {template_id}")
                return None
            
            # Prepare user information
            user_info = self._format_resume_data_for_llm(resume_data, user_text)
            logger.info(f"[generate_resume_latex] Formatted user info for LLM")
            print(f"[generate_resume_latex] Formatted user info for LLM")
            
            # Create LLM prompt
            prompt = self._create_resume_generation_prompt(user_info, template_latex, template.name)
            logger.info(f"[generate_resume_latex] Created LLM prompt")
            print(f"[generate_resume_latex] Created LLM prompt")
            
            # Create LLM client (using Claude for resume generation)
            try:
                logger.info(f"[generate_resume_latex] Creating Claude LLM client")
                print(f"[generate_resume_latex] Creating Claude LLM client")
                print(ANTHROPIC_API_KEY)
                llm_client = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    anthropic_api_key=ANTHROPIC_API_KEY,
                    temperature=0.1,
                    max_tokens=4000
                )
                logger.info(f"[generate_resume_latex] Claude LLM client created")
                print(f"[generate_resume_latex] Claude LLM client created")
            except Exception as e:
                logger.error(f"Error creating Claude LLM client: {e}")
                print(f"Error creating Claude LLM client: {e}")
                # Fallback to Gemini if Claude fails
                try:
                    logger.info(f"[generate_resume_latex] Creating Gemini LLM client as fallback")
                    print(f"[generate_resume_latex] Creating Gemini LLM client as fallback")
                    print(GEMINI_API_KEY)
                    llm_client = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash",
                        google_api_key=GEMINI_API_KEY,
                        temperature=0.1,
                        max_tokens=4000
                    )
                    logger.info("Using Gemini as fallback for resume generation")
                    print("Using Gemini as fallback for resume generation")
                except Exception as fallback_error:
                    logger.error(f"Error creating fallback Gemini client: {fallback_error}")
                    print(f"Error creating fallback Gemini client: {fallback_error}")
                    return None
            
            logger.info(f"[generate_resume_latex] Invoking LLM client")
            print(f"[generate_resume_latex] Invoking LLM client")
            response = llm_client.invoke(prompt)
            logger.info(f"[generate_resume_latex] LLM client invocation complete")
            print(f"[generate_resume_latex] LLM client invocation complete")
            
            # Parse LLM response
            try:
                # Extract JSON from response
                response_text = response.content if hasattr(response, 'content') else str(response)
                logger.info(f"[generate_resume_latex] Got response from LLM client")
                print(f"[generate_resume_latex] Got response from LLM client")
                print("raw response:", response_text)
                
                # Clean the response text to remove problematic control characters
                cleaned_response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response_text)
                
                # Find JSON in the response
                start_idx = cleaned_response_text.find('{')
                end_idx = cleaned_response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = cleaned_response_text[start_idx:end_idx]
                    llm_data = json.loads(json_str)
                    logger.info(f"[generate_resume_latex] Parsed JSON from LLM response")
                    print(f"[generate_resume_latex] Parsed JSON from LLM response")
                    
                    return LLMResumeResponse(
                        template_used=llm_data.get("template_used", template.name),
                        latex_code=llm_data.get("latex_code", ""),
                        extracted_info=llm_data.get("extracted_info", {}),
                        missing_info=llm_data.get("missing_info", [])
                    )
                else:
                    logger.error("No JSON found in LLM response")
                    print("No JSON found in LLM response")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response JSON: {e}")
                print(f"Error parsing LLM response JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating resume LaTeX: {e}")
            print(f"Error generating resume LaTeX: {e}")
            return None
    
    def _format_resume_data_for_llm(self, resume_data: ResumeData, user_text: str = "") -> str:
        """Format resume data for LLM input"""
        formatted_text = []
        
        # Personal info
        personal = resume_data.personal_info
        formatted_text.append(f"Name: {personal.name}")
        formatted_text.append(f"Email: {personal.email}")
        if personal.phone:
            formatted_text.append(f"Phone: {personal.phone}")
        if personal.location:
            formatted_text.append(f"Location: {personal.location}")
        if personal.linkedin:
            formatted_text.append(f"LinkedIn: {personal.linkedin}")
        if personal.github:
            formatted_text.append(f"GitHub: {personal.github}")
        if personal.portfolio:
            formatted_text.append(f"Portfolio: {personal.portfolio}")
        if personal.summary:
            formatted_text.append(f"Summary: {personal.summary}")
        
        # Education
        if resume_data.education:
            formatted_text.append("\nEducation:")
            for edu in resume_data.education:
                formatted_text.append(f"- {edu.degree} from {edu.institution}")
                if edu.graduation_date:
                    formatted_text.append(f"  Graduated: {edu.graduation_date}")
                if edu.gpa:
                    formatted_text.append(f"  GPA: {edu.gpa}")
        
        # Experience
        if resume_data.experience:
            formatted_text.append("\nExperience:")
            for exp in resume_data.experience:
                formatted_text.append(f"- {exp.title} at {exp.company}")
                formatted_text.append(f"  Period: {exp.start_date} - {exp.end_date or 'Present'}")
                for desc in exp.description:
                    formatted_text.append(f"  • {desc}")
        
        # Projects
        if resume_data.projects:
            formatted_text.append("\nProjects:")
            for proj in resume_data.projects:
                formatted_text.append(f"- {proj.name}: {proj.description}")
                formatted_text.append(f"  Technologies: {', '.join(proj.technologies)}")
                if proj.url:
                    formatted_text.append(f"  URL: {proj.url}")
        
        # Skills
        skills = resume_data.skills
        formatted_text.append("\nSkills:")
        if skills.programming_languages:
            formatted_text.append(f"Programming Languages: {', '.join(skills.programming_languages)}")
        if skills.frameworks:
            formatted_text.append(f"Frameworks: {', '.join(skills.frameworks)}")
        if skills.tools:
            formatted_text.append(f"Tools: {', '.join(skills.tools)}")
        if skills.soft_skills:
            formatted_text.append(f"Soft Skills: {', '.join(skills.soft_skills)}")
        
        # Add user text if provided
        if user_text:
            formatted_text.append(f"\nAdditional Information: {user_text}")
        
        return "\n".join(formatted_text)
    
    def _create_resume_generation_prompt(self, user_info: str, template_latex: str, template_name: str) -> str:
        """Create the LLM prompt for resume generation"""
        return f"""
You are a professional resume formatter that converts unstructured user information into clean LaTeX code based on a provided example resume template.

Input Format:
User Info (unformatted string): {user_info}

Example LaTeX Code:
{template_latex}

Resume Template Name: {template_name}

Your Task:
1. Parse the unformatted user info and extract:
   - Personal details (name, email, phone, location, links)
   - Work experience (positions, companies, dates, achievements)
   - Education (degrees, schools, graduation dates, GPA if mentioned)
   - Skills (technical skills, programming languages, tools)
   - Projects (if mentioned)

2. Analyze the example LaTeX template to understand:
   - Document structure and packages used
   - Formatting styles for each section
   - Color schemes and typography
   - Section ordering and layout

3. Generate new LaTeX code that:
   - Follows the exact same structure and styling as the example
   - Replaces the example content with the user's parsed information
   - Maintains all formatting, colors, and design elements
   - Handles missing information gracefully (skip sections if no relevant data)

Output Format:
Return a JSON object with this exact structure:
{{
  "template_used": "{template_name}",
  "latex_code": "Complete LaTeX document code here - must be ready to compile",
  "extracted_info": {{
    "personal": "What personal info was found",
    "experience_count": "Number of jobs found",
    "education_count": "Number of education entries",
    "skills_found": "List of skills identified",
    "projects_count": "Number of projects found",
    "links_found": ["List of URLs/links identified and their context"]
  }},
  "missing_info": ["List of sections that couldn't be filled due to missing data"]
}}

Processing Guidelines:
- Be flexible with input formats
- Infer missing details when possible
- Handle typos and informal language
- Extract dates in various formats
- Parse skills from context
- Extract and embed links properly using \\href{{url}}{{display_text}}
- Preserve all styling and document structure
- Ensure LaTeX compiles without errors
- No placeholder text - only include actual user information
- Professional formatting with proper spacing and alignment
- One page preferred unless user has extensive experience

Generate the LaTeX code now:
"""
    
    def generate_pdf(self, latex_code: str, template_name: str) -> PDFGenerationResponse:
        """Generate PDF from LaTeX code using latexonline.cc API"""
        try:
            # Clean and validate LaTeX code
            cleaned_latex = self._clean_latex_code(latex_code)
            
            # Prepare request to latexonline.cc
            url = "https://latexonline.cc/data"
            data = {
                "code": cleaned_latex,
                "format": "pdf"
            }
            
            # Make request with better error handling
            response = requests.post(url, data=data, timeout=60)
            
            if response.status_code == 200:
                # Check if response contains PDF data
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type or len(response.content) > 1000:
                    return PDFGenerationResponse(
                        success=True,
                        message="PDF generated successfully",
                        pdf_data=response.content,
                        pdf_url=None
                    )
                else:
                    # Response might be an error page
                    return PDFGenerationResponse(
                        success=False,
                        message="PDF generation failed: Invalid response",
                        error_message="API returned non-PDF content"
                    )
            else:
                # Try to get error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                
                return PDFGenerationResponse(
                    success=False,
                    message=f"PDF generation failed: {error_msg}",
                    error_message=error_msg
                )
                
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return PDFGenerationResponse(
                success=False,
                message="PDF generation failed",
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and validate LaTeX code for better compatibility"""
        try:
            # Remove any potential JSON artifacts
            if latex_code.startswith('```latex'):
                latex_code = latex_code.replace('```latex', '').replace('```', '')
            
            # Ensure proper document structure
            if '\\documentclass' not in latex_code:
                # Add basic document structure if missing
                latex_code = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{hyperref}}
\\usepackage{{color}}
\\usepackage{{enumitem}}
\\usepackage{{array}}
\\usepackage{{tabularx}}
\\usepackage{{booktabs}}
\\usepackage{{xcolor}}

\\begin{{document}}
{latex_code}
\\end{{document}}"""
            
            # Fix common LaTeX issues
            latex_code = latex_code.replace('\\href{', '\\href{')
            latex_code = latex_code.replace('\\url{', '\\url{')
            
            # Ensure document ends properly
            if not latex_code.strip().endswith('\\end{document}'):
                latex_code += '\n\\end{document}'
            
            return latex_code
            
        except Exception as e:
            logger.warning(f"Error cleaning LaTeX code: {e}")
            return latex_code
    
    def generate_pdf_fallback(self, latex_code: str, template_name: str) -> PDFGenerationResponse:
        """Fallback PDF generation using a different service"""
        try:
            # Try using overleaf API or another service
            url = "https://www.overleaf.com/api/v1/project"
            
            # For now, return a helpful error message
            return PDFGenerationResponse(
                success=False,
                message="PDF generation service temporarily unavailable",
                error_message="Please try again later or download the LaTeX code to compile locally"
            )
            
        except Exception as e:
            logger.error(f"Error in fallback PDF generation: {e}")
            return PDFGenerationResponse(
                success=False,
                message="PDF generation failed",
                error_message=f"All PDF services are currently unavailable: {str(e)}"
            )

# Global instance
resume_builder_service = ResumeBuilderService() 