#!/usr/bin/env python3
"""
Test script for Resume Builder system
"""
import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_resume_builder():
    """Test the resume builder functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Resume Builder System...")
    
    # Test 1: Get templates
    print("\n1. Testing template listing...")
    try:
        response = requests.get(f"{base_url}/resume-builder/templates")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            print(f"✅ Found {len(templates)} templates:")
            for template in templates:
                print(f"   - {template['name']} ({template['category']})")
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return False
    
    if not templates:
        print("❌ No templates found")
        return False
    
    template_id = templates[0]['id']
    
    # Test 2: Get specific template
    print(f"\n2. Testing template details for {template_id}...")
    try:
        response = requests.get(f"{base_url}/resume-builder/templates/{template_id}")
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template details: {template['name']}")
        else:
            print(f"❌ Failed to get template: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting template: {e}")
        return False
    
    # Test 3: Build resume from form data
    print(f"\n3. Testing resume generation from form data...")
    
    sample_resume_data = {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 (555) 123-4567",
            "location": "San Francisco, CA",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "portfolio": "https://johndoe.dev",
            "summary": "Experienced software engineer with 5+ years in full-stack development"
        },
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "Stanford University",
                "location": "Stanford, CA",
                "graduation_date": "May 2020",
                "gpa": "3.8/4.0",
                "relevant_courses": ["Data Structures", "Algorithms", "Software Engineering"]
            }
        ],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "start_date": "June 2020",
                "end_date": "Present",
                "description": [
                    "Led development of microservices architecture serving 1M+ users",
                    "Mentored 3 junior developers and conducted code reviews",
                    "Improved system performance by 40% through optimization"
                ],
                "technologies": ["Python", "React", "AWS", "Docker"]
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform with payment integration",
                "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
                "url": "https://ecommerce-demo.com",
                "github": "https://github.com/johndoe/ecommerce"
            }
        ],
        "skills": {
            "technical_skills": ["System Design", "API Development", "Database Design"],
            "programming_languages": ["Python", "JavaScript", "Java", "SQL"],
            "frameworks": ["React", "Django", "Spring Boot", "Express.js"],
            "tools": ["Git", "Docker", "AWS", "Jenkins"],
            "soft_skills": ["Leadership", "Communication", "Problem Solving"]
        },
        "certifications": ["AWS Certified Developer", "Google Cloud Professional"],
        "languages": ["English (Native)", "Spanish (Fluent)"]
    }
    
    build_request = {
        "template_id": template_id,
        "input_method": "form",
        "resume_data": sample_resume_data
    }
    
    try:
        response = requests.post(
            f"{base_url}/resume-builder/build",
            json=build_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume generated successfully!")
            print(f"   Template used: {result.get('template_used')}")
            print(f"   LaTeX code length: {len(result.get('latex_code', ''))} characters")
            
            # Check extracted info
            extracted_info = result.get('data', {}).get('extracted_info', {})
            print(f"   Personal info found: {extracted_info.get('personal', 'Yes')}")
            print(f"   Experience entries: {extracted_info.get('experience_count', '0')}")
            print(f"   Education entries: {extracted_info.get('education_count', '0')}")
            print(f"   Projects found: {extracted_info.get('projects_count', '0')}")
            
            # Check missing info
            missing_info = result.get('data', {}).get('missing_info', [])
            if missing_info:
                print(f"   Missing info: {', '.join(missing_info)}")
            else:
                print("   No missing information")
                
        else:
            print(f"❌ Failed to generate resume: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating resume: {e}")
        return False
    
    # Test 4: Generate PDF from LaTeX
    print(f"\n4. Testing PDF generation...")
    
    sample_latex = r"""
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

\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries\color{black}
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\begin{document}

\begin{center}
    \textbf{\Huge \scshape John Doe} \\ \vspace{3pt}
    \small
    \faIcon{phone} +1 (555) 123-4567 $|$ 
    \faIcon{envelope} \href{mailto:john.doe@example.com}{john.doe@example.com} $|$ 
    \faIcon{map-marker-alt} San Francisco, CA $|$ 
    \faIcon{github} \href{https://github.com/johndoe}{github.com/johndoe} $|$
    \faIcon{linkedin} \href{https://linkedin.com/in/johndoe}{linkedin.com/in/johndoe}
\end{center}

\section{Education}
  \begin{itemize}[leftmargin=0.15in, label={}]
    \item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{Stanford University} & May 2020 \\
      \textit{Bachelor of Science in Computer Science} & \textit{GPA: 3.8/4.0} \\
    \end{tabular*}\vspace{-5pt}
  \end{itemize}

\section{Experience}
  \begin{itemize}[leftmargin=0.15in, label={}]
    \item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{Tech Corp} & San Francisco, CA \\
      \textit{Senior Software Engineer} & \textit{June 2020 - Present} \\
    \end{tabular*}\vspace{-7pt}
    \begin{itemize}
      \item Led development of microservices architecture serving 1M+ users
      \item Mentored 3 junior developers and conducted code reviews
      \item Improved system performance by 40\% through optimization
    \end{itemize}
  \end{itemize}

\section{Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{Languages:} Python, JavaScript, Java, SQL \\
    \textbf{Frameworks:} React, Django, Spring Boot, Express.js \\
    \textbf{Tools:} Git, Docker, AWS, Jenkins
    }}
 \end{itemize}

\end{document}
"""
    
    pdf_request = {
        "latex_code": sample_latex,
        "template_name": "Test Template"
    }
    
    try:
        response = requests.post(
            f"{base_url}/resume-builder/generate-pdf",
            json=pdf_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ PDF generated successfully!")
                if result.get('pdf_data'):
                    print(f"   PDF data size: {len(result['pdf_data'])} bytes")
                else:
                    print("   No PDF data returned")
            else:
                print(f"❌ PDF generation failed: {result.get('message')}")
                print(f"   Error: {result.get('error_message')}")
        else:
            print(f"❌ Failed to generate PDF: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
    
    print("\n🎉 Resume Builder System Test Complete!")
    return True

if __name__ == "__main__":
    test_resume_builder() 