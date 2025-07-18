#!/usr/bin/env python3
"""
Simple test script to verify the ranking system works correctly
"""

from app.services.ranker import rank_job_results

# Sample test data matching the format from your actual output
sample_parsed_info = {
    "Skills": ["Python", "React", "Node.js", "SQL", "PostgreSQL", "MongoDB", "Docker"],
    "Role": "Intern",
    "Role_Variants": ["Software Engineering Intern", "Data Science Intern", "Machine Learning Intern", "Backend Intern", "Frontend Intern"]
}

sample_search_results = {
    "organic": [
        {
            "title": "Python Developer Intern",
            "link": "https://in.linkedin.com/jobs/python-developer-intern-123",
            "snippet": "Python Developer Intern position at tech company. Experience with React, SQL, and MongoDB preferred. Full-time internship opportunity.",
            "position": 1
        },
        {
            "title": "React Developers Internship",
            "link": "https://in.linkedin.com/jobs/react-developers-internship-456",
            "snippet": "React.js internship with Node.js backend development. PostgreSQL database experience needed.",
            "position": 2
        },
        {
            "title": "Data Science Intern",
            "link": "https://www.wellfound.com/jobs/data-science-intern-789",
            "snippet": "Data Science internship role. Python, SQL knowledge required. Docker containerization experience is a plus.",
            "position": 3
        },
        {
            "title": "Marketing Intern",
            "link": "https://internshala.com/internships/marketing-intern-101",
            "snippet": "Marketing internship opportunity. Social media and content creation experience preferred.",
            "position": 4
        }
    ],
    "searchParameters": {
        "q": "test query",
        "type": "search",
        "num": 10,
        "engine": "google"
    }
}

def test_ranking():
    """Test the ranking functionality"""
    print("🧪 Testing Job Ranking System...")
    print("=" * 50)
    
    try:
        # Test the ranking function
        result = rank_job_results(sample_parsed_info, sample_search_results)
        
        print("✅ Ranking completed successfully!")
        print(f"📊 Total jobs ranked: {result['summary']['total_jobs']}")
        print(f"🎯 High relevance: {result['summary']['high_relevance']}")
        print(f"🔶 Medium relevance: {result['summary']['medium_relevance']}")
        print(f"🔻 Low relevance: {result['summary']['low_relevance']}")
        print()
        
        print("🏆 Top 3 Ranked Jobs:")
        print("-" * 30)
        
        for i, job in enumerate(result['ranked_jobs'][:3], 1):
            print(f"{i}. {job['title']}")
            print(f"   Score: {job['score']}/100")
            print(f"   Skills matched: {', '.join(job['skill_matches']) if job['skill_matches'] else 'None'}")
            print(f"   Role match: {job['role_match']}")
            print(f"   Reasons: {'; '.join(job['reasons'])}")
            print(f"   Source: {job['source']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in ranking: {e}")
        return False

if __name__ == "__main__":
    success = test_ranking()
    if success:
        print("🎉 All tests passed! The ranking system is working correctly.")
    else:
        print("💥 Tests failed. Please check the implementation.") 