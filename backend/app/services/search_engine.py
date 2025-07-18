import os
import requests
import re

from app.core.config import SERPER_API_KEY

def extract_quotable_terms(query: str) -> list:
    """
    Extract technical terms that should be quoted for better search results
    Only quotes specific technical terms, max 2 words each
    
    Args:
        query: Search query string
    
    Returns:
        List of terms that should be quoted
    """
    quotable_terms = []
    query_lower = query.lower()
    
    # Technical terms that should be quoted (max 2 words)
    tech_keywords = [
        "ai", "ml", "llm", "nlp", "cv", "dl",  # AI/ML terms
        "react", "angular", "vue", "node", "django", "flask",  # Frameworks
        "python", "java", "javascript", "golang", "rust",  # Languages
        "aws", "gcp", "azure", "docker", "kubernetes",  # Cloud/DevOps
        "sql", "nosql", "mongodb", "redis", "kafka",  # Databases
        "machine learning", "artificial intelligence", "deep learning",  # 2-word AI terms
        "data science", "data engineering", "full stack",  # 2-word role terms
    ]
    
    for term in tech_keywords:
        if term in query_lower:
            quotable_terms.append(term)
    
    # Limit to avoid too many quoted terms
    return quotable_terms[:2]

def remove_quotable_terms(query: str, quotable_terms: list) -> str:
    """
    Remove quotable terms from query to create base query
    
    Args:
        query: Original query string
        quotable_terms: Terms to remove (they'll be quoted separately)
    
    Returns:
        Base query string without quotable terms
    """
    base_query = query
    
    for term in quotable_terms:
        # Remove the term (case insensitive)
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        base_query = pattern.sub('', base_query)
    
    # Clean up extra spaces
    base_query = ' '.join(base_query.split())
    
    return base_query

def search_jobs(query: str, location: str = "Bengaluru", num_results: int = 20, experience_level: str = None, job_type: str = None) -> dict:
    """
    Search for jobs using simplified, effective queries
    Restricted to specific job sites: LinkedIn, Naukri, Indeed, Internshala, Wellfound
    
    Args:
        query: Job search query (role, skills, etc.)
        location: Location for job search
        num_results: Number of results to return per query
        experience_level: User's experience level preference (entry, mid, senior)
        job_type: User's job type preference (full-time, part-time, internship, contract)
    
    Returns:
        Dictionary with job search results
    """
    try:
        # Create simplified search queries for better results
        job_queries = []
        
        # Extract technical terms that should be quoted (max 2 words)
        tech_terms = extract_quotable_terms(query)
        base_query = remove_quotable_terms(query, tech_terms)
        
        # Core job sites with simplified queries
        if tech_terms and base_query.strip():
            # Include first technical term in quotes, keep it simple
            tech_term = tech_terms[0]  # Use only the first/most important term
            job_queries.extend([
                f'site:linkedin.com/jobs {base_query} "{tech_term}" {location}',
                f'site:naukri.com {base_query} "{tech_term}" {location}',
                f'site:indeed.com {base_query} "{tech_term}" {location}',
                f'site:wellfound.com {base_query} "{tech_term}" {location}',
            ])
        elif tech_terms:
            # Only tech term, no base query
            tech_term = tech_terms[0]
            job_queries.extend([
                f'site:linkedin.com/jobs "{tech_term}" engineer {location}',
                f'site:naukri.com "{tech_term}" developer {location}',
                f'site:indeed.com "{tech_term}" {location}',
                f'site:wellfound.com "{tech_term}" {location}',
            ])
        else:
            # Simple role-based queries without quotes
            job_queries.extend([
                f'site:linkedin.com/jobs {base_query} {location}',
                f'site:naukri.com {base_query} {location}',
                f'site:indeed.com {base_query} {location}',
                f'site:wellfound.com {base_query} {location}',
            ])
        
        # Add experience-level specific queries
        if experience_level == "senior":
            job_queries.extend([
                f'site:linkedin.com/jobs "SDE III" {location}',
                f'site:naukri.com "Senior Engineer" {location}',
            ])
        elif experience_level == "mid":
            job_queries.extend([
                f'site:linkedin.com/jobs "SDE II" {location}',
                f'site:naukri.com "Software Engineer" {location}',
            ])
        elif experience_level == "entry":
            job_queries.extend([
                f'site:linkedin.com/jobs "SDE" {location}',
                f'site:naukri.com "Software Developer" {location}',
            ])
        
        # Only include Internshala for internship searches
        if job_type == "internship":
            job_queries.append(f'site:internshala.com {base_query} intern {location}')
        
        # Debug log to show simplified queries
        print(f"[SEARCH DEBUG] Generated {len(job_queries)} simplified queries:")
        for i, q in enumerate(job_queries[:3]):  # Show first 3 queries
            print(f"  Query {i+1}: {q}")
        if len(job_queries) > 3:
            print(f"  ... and {len(job_queries) - 3} more queries")
        
        # Use the existing search function with deduplication
        results = search_google_with_deduplication(job_queries, num_results)
        
        # Add job-specific metadata
        results["search_metadata"] = {
            "query": query,
            "location": location,
            "num_results": num_results,
            "search_type": "job_search"
        }
        
        return results
        
    except Exception as e:
        print(f"Error in search_jobs: {e}")
        return {
            "organic": [],
            "summary": {
                "total_jobs": 0,
                "queries_processed": 0,
                "job_boards_targeted": [],
                "query_types": []
            },
            "search_metadata": {
                "query": query,
                "location": location,
                "num_results": num_results,
                "search_type": "job_search",
                "error": str(e)
            }
        }

def search_google(queries, num_results=10):
    """
    Search Google with enhanced query format support
    
    Args:
        queries: Can be either:
                - List of query strings (old format)
                - List of query objects with metadata (new format)
        num_results: Number of results per query
    
    Returns:
        Dictionary with search results and metadata
    """
    all_results = {}
    aggregated_organic = []
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Handle both old and new query formats
    processed_queries = []
    for query in queries:
        if isinstance(query, dict):
            # New format: extract query string and metadata
            query_string = query.get("query", "")
            query_meta = {
                "query": query_string,
                "type": query.get("type", "Unknown"),
                "job_board": query.get("job_board", "Unknown"),
                "focus": query.get("focus", "General search"),
                "role_match": query.get("role_match", "Unknown")
            }
        else:
            # Old format: just query string
            query_string = query
            query_meta = {
                "query": query_string,
                "type": "Legacy Query",
                "job_board": "Unknown",
                "focus": "General search",
                "role_match": "Unknown"
            }
        
        processed_queries.append(query_meta)
    
    for i, query_meta in enumerate(processed_queries):
        query_string = query_meta["query"]
        
        payload = {
            "q": query_string,
            "num": num_results
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response for query {i+1} ({query_meta['type']}): {response.json()}")
            response.raise_for_status()
            query_results = response.json()
            
            if i == 0:
                # Keep the first query's metadata
                all_results["searchParameters"] = query_results.get("searchParameters", {})
                all_results["credits"] = query_results.get("credits", 0)
                if query_results.get("organic", []):
                    print("example_snippet", query_results.get("organic", [])[0].get("snippet"))
            
            # Extract and store jobs from this query
            organic_jobs = query_results.get("organic", [])
            for item in organic_jobs:
                if item.get("link"):  # Only include valid jobs with links
                    # Add query metadata to each job result
                    enhanced_item = {
                        **item,
                        "query_type": query_meta["type"],
                        "target_job_board": query_meta["job_board"],
                        "query_focus": query_meta["focus"],
                        "role_match": query_meta["role_match"],
                        "source_query": query_string
                    }
                    aggregated_organic.append(enhanced_item)
            
            # Store jobs for this specific query with enhanced metadata
            all_results[query_string] = {
                "query_metadata": query_meta,
                "results": [
                    {
                        "title": item.get("title"),
                        "url": item.get("link"),
                        "snippet": item.get("snippet"),
                        "source": item.get("link", "").split("/")[2] if item.get("link") else "unknown",
                        "query_type": query_meta["type"],
                        "target_job_board": query_meta["job_board"],
                        "query_focus": query_meta["focus"],
                        "role_match": query_meta["role_match"]
                    }
                    for item in organic_jobs
                ]
            }
            
            print(f"Query '{query_string}' ({query_meta['type']}) found {len(organic_jobs)} results")
            
        except Exception as e:
            print(f"Error searching query '{query_string}' ({query_meta['type']}): {e}")
            # Continue with other queries even if one fails
            all_results[query_string] = {
                "query_metadata": query_meta,
                "results": []
            }
    
    # Set the aggregated organic results
    all_results["organic"] = aggregated_organic
    
    # Add summary statistics
    all_results["summary"] = {
        "total_jobs": len(aggregated_organic),
        "queries_processed": len(processed_queries),
        "job_boards_targeted": list(set(q["job_board"] for q in processed_queries)),
        "query_types": list(set(q["type"] for q in processed_queries))
    }
    
    print(f"Total jobs found across all queries: {len(aggregated_organic)}")
    print(f"Job boards targeted: {all_results['summary']['job_boards_targeted']}")
    print(f"Query types used: {all_results['summary']['query_types']}")
    
    return all_results

def search_google_with_deduplication(queries, num_results=10):
    """
    Enhanced search function with deduplication based on job URLs
    
    Args:
        queries: List of query strings or query objects
        num_results: Number of results per query
    
    Returns:
        Dictionary with deduplicated search results
    """
    results = search_google(queries, num_results)
    
    # Deduplicate based on URL
    seen_urls = set()
    deduplicated_organic = []
    
    for item in results.get("organic", []):
        url = item.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduplicated_organic.append(item)
    
    results["organic"] = deduplicated_organic
    results["summary"]["total_jobs"] = len(deduplicated_organic)
    results["summary"]["duplicates_removed"] = len(results.get("organic", [])) - len(deduplicated_organic)
    
    print(f"Deduplication: {results['summary']['duplicates_removed']} duplicates removed")
    print(f"Final unique jobs: {len(deduplicated_organic)}")
    
    return results

def analyze_search_results(results):
    """
    Analyze search results to provide insights
    
    Args:
        results: Results from search_google function
    
    Returns:
        Dictionary with analysis insights
    """
    organic_results = results.get("organic", [])
    
    if not organic_results:
        return {"message": "No results to analyze"}
    
    # Analyze by job board
    job_board_stats = {}
    query_type_stats = {}
    role_match_stats = {}
    
    for item in organic_results:
        # Job board analysis
        target_board = item.get("target_job_board", "Unknown")
        job_board_stats[target_board] = job_board_stats.get(target_board, 0) + 1
        
        # Query type analysis
        query_type = item.get("query_type", "Unknown")
        query_type_stats[query_type] = query_type_stats.get(query_type, 0) + 1
        
        # Role match analysis
        role_match = item.get("role_match", "Unknown")
        role_match_stats[role_match] = role_match_stats.get(role_match, 0) + 1
    
    analysis = {
        "total_results": len(organic_results),
        "job_board_distribution": dict(sorted(job_board_stats.items(), key=lambda x: x[1], reverse=True)),
        "query_type_distribution": dict(sorted(query_type_stats.items(), key=lambda x: x[1], reverse=True)),
        "role_match_distribution": dict(sorted(role_match_stats.items(), key=lambda x: x[1], reverse=True)),
        "top_performing_queries": []
    }
    
    # Find top performing queries
    query_performance = {}
    for query_key, query_data in results.items():
        if query_key not in ["organic", "searchParameters", "credits", "summary"]:
            if isinstance(query_data, dict) and "results" in query_data:
                query_performance[query_key] = len(query_data["results"])
    
    analysis["top_performing_queries"] = sorted(
        query_performance.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]
    
    return analysis