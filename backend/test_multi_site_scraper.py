#!/usr/bin/env python3
"""
Multi-Site Job Scraper Test
Quick verification that the scraper works with all supported job sites
"""

import asyncio
from app.services.scraper import scrape_job, scrape_multiple_jobs, get_safe_config, get_proxy_config

async def test_multi_site_scraper():
    """Test scraper with different job sites"""
    
    print("🔍 Multi-Site Job Scraper Test")
    print("=" * 50)
    
    # Test URLs for different job sites
    test_jobs = [
        {
            'site': 'LinkedIn',
            'url': 'https://in.linkedin.com/jobs/intern-software-development-jobs-bengaluru?position=1&pageNum=0'
        },
        # Add other site URLs when available for testing
        # {
        #     'site': 'Naukri',
        #     'url': 'https://www.naukri.com/job-listings-software-developer-...'
        # },
        # {
        #     'site': 'Indeed',
        #     'url': 'https://in.indeed.com/viewjob?jk=...'
        # },
        # {
        #     'site': 'Wellfound',
        #     'url': 'https://wellfound.com/jobs/...'
        # },
        # {
        #     'site': 'Internshala',
        #     'url': 'https://internshala.com/internship/detail/...'
        # }
    ]
    
    print(f"Testing {len(test_jobs)} job site(s)...")
    
    for i, job in enumerate(test_jobs, 1):
        print(f"\n{i}. Testing {job['site']}:")
        print(f"   URL: {job['url'][:80]}...")
        
        try:
            result = await scrape_job(job['url'], headless=False)  # Show browser for testing
            
            if result['success']:
                print(f"   ✅ Success!")
                print(f"   Site: {result['site']}")
                print(f"   Title: {result['title']}")
                print(f"   Company: {result['company']}")
                print(f"   Location: {result['location']}")
                print(f"   Description: {len(result['description'])} characters")
                print(f"   Modal handled: {result['modal_closed']}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n✅ Multi-site scraper test completed!")

if __name__ == "__main__":
    asyncio.run(test_multi_site_scraper()) 