import os
import requests
import re
import time
from datetime import datetime, timedelta

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

def parse_job_date(date_str: str) -> float:
    """
    Parse job posting dates from various formats into timestamp
    
    Args:
        date_str: Date string like "2 days ago", "1 week ago", "Jun 24, 2025", etc.
        
    Returns:
        Timestamp in seconds, or None if can't parse
    """
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    current_time = time.time()
    
    try:
        # Handle relative dates like "2 days ago", "1 week ago", etc.
        if "ago" in date_str:
            if "day" in date_str:
                # Extract number of days
                days_match = re.search(r'(\d+)\s*days?\s*ago', date_str)
                if days_match:
                    days = int(days_match.group(1))
                    return current_time - (days * 24 * 60 * 60)
            
            elif "week" in date_str:
                # Extract number of weeks
                weeks_match = re.search(r'(\d+)\s*weeks?\s*ago', date_str)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    return current_time - (weeks * 7 * 24 * 60 * 60)
            
            elif "month" in date_str:
                # Extract number of months
                months_match = re.search(r'(\d+)\s*months?\s*ago', date_str)
                if months_match:
                    months = int(months_match.group(1))
                    return current_time - (months * 30 * 24 * 60 * 60)  # Approximate
            
            elif "hour" in date_str:
                # Extract number of hours
                hours_match = re.search(r'(\d+)\s*hours?\s*ago', date_str)
                if hours_match:
                    hours = int(hours_match.group(1))
                    return current_time - (hours * 60 * 60)
        
        # Handle absolute dates like "Jun 24, 2025", "Jul 11, 2025"
        elif any(month in date_str for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                                                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            # Try to parse dates like "Jun 24, 2025"
            for fmt in ['%b %d, %Y', '%B %d, %Y', '%b %d %Y', '%B %d %Y']:
                try:
                    dt = datetime.strptime(date_str, fmt.lower())
                    return dt.timestamp()
                except ValueError:
                    continue
        
        # If we can't parse it, return current time (include the job)
        return current_time
        
    except Exception as e:
        print(f"[DATE PARSE ERROR] Could not parse '{date_str}': {e}")
        return current_time  # Include job if we can't parse date

def search_jobs(query: str, location: str = "Bengaluru", num_results: int = 20, experience_level: str = None, job_type: str = None, max_job_age_days: int = 90, search_scope: str = "job_boards") -> dict:
    """
    Search for jobs using specific, targeted queries for individual job listings
    Focus on getting specific job posts, not aggregated results
    
    Args:
        query: Job search query (role, skills, etc.)
        location: Location for job search
        num_results: Number of results to return per query
        experience_level: User's experience level preference (entry, mid, senior)
        job_type: User's job type preference (full-time, part-time, internship, contract)
        max_job_age_days: Maximum age of job postings in days (default: 90 days / 3 months)
        search_scope: Search scope - "job_boards", "company_pages", or "comprehensive"
    
    Returns:
        Dictionary with job search results
    """
    try:
        # Create specific, targeted search queries for individual job listings
        job_queries = []
        
        # Extract technical terms that should be quoted (max 2 words)
        tech_terms = extract_quotable_terms(query)
        base_query = remove_quotable_terms(query, tech_terms)
        
        print(f"[SEARCH ENGINE] Using search scope: {search_scope}")
        
        # 1. MAJOR JOB BOARDS - Always include these for job_boards and comprehensive scope
        if search_scope in ["job_boards", "comprehensive"]:
            print(f"[SEARCH ENGINE] Adding job board queries...")
            if tech_terms and base_query.strip():
                # Target specific job listing URLs, not search aggregation pages
                tech_term = tech_terms[0]
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ {base_query} "{tech_term}" {location}',
                    f'site:naukri.com/job-listings {base_query} "{tech_term}" {location}',
                    f'site:indeed.com/viewjob {base_query} "{tech_term}" {location}',
                    f'site:wellfound.com/jobs/ {base_query} "{tech_term}" {location}',
                    # Add more specific patterns
                    f'inurl:linkedin.com/jobs/view {base_query} {location}',
                    f'inurl:naukri.com/job-listings {base_query} {location}',
                ])
            elif tech_terms:
                # Only tech term, target job listing pages
                tech_term = tech_terms[0]
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ "{tech_term}" engineer {location}',
                    f'site:naukri.com/job-listings "{tech_term}" developer {location}',
                    f'site:indeed.com/viewjob "{tech_term}" {location}',
                    f'site:wellfound.com/jobs/ "{tech_term}" {location}',
                ])
            else:
                # Simple role-based queries targeting specific job pages
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ {base_query} {location}',
                    f'site:naukri.com/job-listings {base_query} {location}',
                    f'site:indeed.com/viewjob {base_query} {location}',
                    f'site:wellfound.com/jobs/ {base_query} {location}',
                ])
            
            # Add specific job title queries for job boards
            if base_query:
                job_queries.extend([
                    f'"{base_query}" site:linkedin.com/jobs/view/ {location} -inurl:search -inurl:results',
                    f'"{base_query}" site:naukri.com -inurl:search -inurl:all-jobs {location}',
                    f'"{base_query}" site:indeed.com/viewjob {location} -"jobs in" -"+ jobs"',
                    f'"{base_query}" site:wellfound.com/jobs/ {location} -inurl:search',
                ])
        
        # 2. COMPANY CAREER PAGES - Include for company_pages and comprehensive scope
        if search_scope in ["company_pages", "comprehensive"]:
            print(f"[SEARCH ENGINE] Adding company career page queries...")
            career_page_patterns = [
                'inurl:careers',
                'inurl:jobs', 
                'inurl:career',
                'inurl:hiring'
            ]
            
            # Add company career page searches
            for pattern in career_page_patterns:
                if tech_terms and base_query.strip():
                    tech_term = tech_terms[0]
                    job_queries.extend([
                        f'{pattern} {base_query} "{tech_term}" {location} -site:linkedin.com -site:indeed.com -site:naukri.com',
                    ])
                else:
                    job_queries.extend([
                        f'{pattern} {base_query} {location} -site:linkedin.com -site:indeed.com -site:naukri.com',
                    ])
            
            # 3. SPECIFIC COMPANY TARGETS - Major tech companies and startups
            target_companies = [
                'google.com', 'microsoft.com', 'amazon.com', 'meta.com', 
                'flipkart.com', 'zomato.com', 'swiggy.com', 'paytm.com',
                'tcs.com', 'infosys.com', 'wipro.com', 'accenture.com'
            ]
            
            # Add specific company searches (limit to avoid too many queries)
            for company in target_companies[:6]:  # Limit to 6 companies
                if tech_terms:
                    tech_term = tech_terms[0]
                    job_queries.append(f'site:{company} careers "{tech_term}" {location}')
                else:
                    job_queries.append(f'site:{company} careers {base_query} {location}')
            
            # 4. ADVANCED COMPANY CAREER PAGE PATTERNS
            advanced_career_patterns = [
                f'inurl:"/careers/" {base_query} {location} -site:linkedin.com -site:indeed.com -site:naukri.com',
                f'inurl:"/jobs/" {base_query} {location} -site:linkedin.com -site:indeed.com -site:naukri.com',
                f'"apply now" {base_query} {location} inurl:careers -site:linkedin.com -site:indeed.com',
                f'"join our team" {base_query} {location} -site:linkedin.com -site:indeed.com'
            ]
            
            job_queries.extend(advanced_career_patterns)
        
        # Experience-level specific queries targeting individual jobs
        if search_scope in ["job_boards", "comprehensive"]:
            if experience_level == "senior":
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ "Senior" {base_query} {location}',
                    f'site:naukri.com/job-listings "Senior" {base_query} {location}',
                ])
            elif experience_level == "mid":
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ {base_query} "2-4 years" {location}',
                    f'site:naukri.com/job-listings {base_query} "3-5 years" {location}',
                ])
            elif experience_level == "entry":
                job_queries.extend([
                    f'site:linkedin.com/jobs/view/ {base_query} "fresher" {location}',
                    f'site:naukri.com/job-listings {base_query} "0-2 years" {location}',
                ])
        
        # Internship-specific queries (only for internship searches)
        if job_type == "internship":
            if search_scope in ["job_boards", "comprehensive"]:
                job_queries.extend([
                    f'site:internshala.com/internship/ {base_query} {location}',
                    f'site:linkedin.com/jobs/view/ "internship" {base_query} {location}',
                ])
            if search_scope in ["company_pages", "comprehensive"]:
                job_queries.extend([
                    f'inurl:careers "internship" {base_query} {location} -site:linkedin.com -site:indeed.com',
                    f'inurl:intern {base_query} {location} -site:linkedin.com -site:indeed.com',
                ])
        
        print(f"[SEARCH ENGINE] Generated {len(job_queries)} queries for scope '{search_scope}'")
        
        # Add negative keywords to exclude aggregated results
        exclusion_terms = [
            '-"jobs in"', 
            '-"+ jobs"', 
            '-"job openings"', 
            '-"job search"',
            '-"all jobs"',
            '-"job results"',
            '-inurl:search',
            '-inurl:all-jobs',
            '-intitle:"jobs"'
        ]
        
        # Apply exclusions to existing queries
        enhanced_queries = []
        for q in job_queries:
            # Add exclusion terms to filter out aggregated results
            enhanced_q = f'{q} {" ".join(exclusion_terms[:3])}'  # Use first 3 exclusions to avoid too long queries
            enhanced_queries.append(enhanced_q)
        
        job_queries = enhanced_queries
        
        # Debug log to show specific queries
        print(f"[SEARCH DEBUG] Generated {len(job_queries)} specific job listing queries:")
        for i, q in enumerate(job_queries[:3]):  # Show first 3 queries
            print(f"  Query {i+1}: {q}")
        if len(job_queries) > 3:
            print(f"  ... and {len(job_queries) - 3} more targeted queries")
        
        # Use the existing search function with deduplication
        results = search_google_with_deduplication(job_queries, num_results)
        
        # Post-process results to filter out aggregated listings and old jobs
        if 'organic' in results:
            filtered_results = []
            current_time = time.time()
            three_months_ago = current_time - (max_job_age_days * 24 * 60 * 60)  # Use max_job_age_days
            
            filtered_counts = {
                'aggregated': 0,
                'job_count': 0,
                'too_old': 0,
                'total_before': len(results['organic']),
                'company_careers': 0,
                'job_boards': 0
            }
            
            for result in results['organic']:
                title = result.get('title', '').lower()
                snippet = result.get('snippet', '').lower()
                url = result.get('link', '').lower()
                
                # Filter out aggregated results based on title patterns
                aggregated_patterns = [
                    'jobs in',
                    '+ jobs',
                    'job openings',
                    'job search',
                    'all jobs',
                    'search results',
                    'job results',
                    'hiring now',
                    'apply now',
                ]
                
                is_aggregated = any(pattern in title for pattern in aggregated_patterns)
                is_aggregated = is_aggregated or any(pattern in snippet[:100] for pattern in aggregated_patterns)
                
                # Also check for number patterns like "2,000+ jobs"
                import re
                has_job_count = re.search(r'\d+[,\d]*\+?\s*(jobs?|openings?)', title + ' ' + snippet)
                
                # Skip known job aggregator pages
                aggregator_domains = [
                    'jobs.', 'career.', 'hiring.', 'recruitment.',
                    'jobsearch.', 'employment.', 'recruit.'
                ]
                is_aggregator = any(domain in url for domain in aggregator_domains)
                
                # Identify job source type
                job_source_type = "unknown"
                if any(board in url for board in ['linkedin.com', 'indeed.com', 'naukri.com', 'wellfound.com', 'internshala.com']):
                    job_source_type = "job_board"
                    filtered_counts['job_boards'] += 1
                elif any(pattern in url for pattern in ['/careers/', '/jobs/', '/career/', '/hiring', '/opportunities']):
                    job_source_type = "company_career_page"
                    filtered_counts['company_careers'] += 1
                elif not is_aggregator:
                    job_source_type = "company_direct"
                    filtered_counts['company_careers'] += 1
                
                # Date filtering - check if job is too old
                is_too_old = False
                job_date = result.get('date')
                if job_date:
                    try:
                        # Parse various date formats
                        job_timestamp = parse_job_date(job_date)
                        if job_timestamp and job_timestamp < three_months_ago:
                            is_too_old = True
                            filtered_counts['too_old'] += 1
                            print(f"[DATE FILTER] Excluded old job: {title[:50]}... (posted: {job_date})")
                    except Exception as e:
                        print(f"[DATE FILTER] Could not parse date '{job_date}': {e}")
                        # If we can't parse the date, include the job (benefit of doubt)
                
                if not is_aggregated and not has_job_count and not is_too_old and not is_aggregator:
                    # Add job source metadata
                    enhanced_result = {
                        **result,
                        'job_source_type': job_source_type,
                        'is_company_direct': job_source_type in ['company_career_page', 'company_direct']
                    }
                    filtered_results.append(enhanced_result)
                elif is_aggregated:
                    filtered_counts['aggregated'] += 1
                    print(f"[FILTER] Excluded aggregated result: {title[:50]}...")
                elif has_job_count:
                    filtered_counts['job_count'] += 1
                    print(f"[FILTER] Excluded job count result: {title[:50]}...")
                elif is_aggregator:
                    print(f"[FILTER] Excluded job aggregator: {title[:50]}...")
            
            results['organic'] = filtered_results
            results['summary']['total_jobs'] = len(filtered_results)
            results['summary']['filtered_aggregated'] = filtered_counts['aggregated'] + filtered_counts['job_count']
            results['summary']['filtered_by_date'] = filtered_counts['too_old']
            results['summary']['max_job_age_days'] = max_job_age_days
            results['summary']['company_career_jobs'] = filtered_counts['company_careers']
            results['summary']['job_board_jobs'] = filtered_counts['job_boards']
            
            print(f"Filtered out {filtered_counts['aggregated']} aggregated results")
            print(f"Filtered out {filtered_counts['job_count']} job count results") 
            print(f"Filtered out {filtered_counts['too_old']} jobs older than {max_job_age_days} days")
            print(f"Found {filtered_counts['company_careers']} company career page jobs")
            print(f"Found {filtered_counts['job_boards']} job board jobs")
            print(f"Final specific job listings: {len(filtered_results)} (from {filtered_counts['total_before']} original)")
        
        # Add job-specific metadata
        results["search_metadata"] = {
            "query": query,
            "location": location,
            "num_results": num_results,
            "search_type": "specific_job_listings",
            "targeting": "individual_jobs_not_aggregated"
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