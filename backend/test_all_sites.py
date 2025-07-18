#!/usr/bin/env python3
"""
Multi-Site Job Scraper Test with Proxy Routing
Tests job description extraction from LinkedIn, Indeed, Internshala, and Wellfound
Shows which proxy each request was routed through
"""

import asyncio
import logging
from app.services.scraper import scrape_job, scrape_multiple_jobs, get_safe_config, get_proxy_config

# Set up logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Example proxy list (replace with your actual proxies)
EXAMPLE_PROXIES = [
    # Add your actual proxy URLs here
    # "http://username:password@proxy1.example.com:8080",
    # "http://username:password@proxy2.example.com:8080",
    # "http://username:password@proxy3.example.com:8080",
]

async def test_single_site(job_info, config=None, show_full_description=False):
    """Test scraping from a single job site"""
    
    print(f"\n🔍 Testing {job_info['site']}:")
    print(f"   URL: {job_info['url']}")
    print("   " + "-" * 60)
    
    try:
        result = await scrape_job(job_info['url'], config=config, headless=True)
        
        if result['success']:
            print(f"   ✅ SUCCESS!")
            print(f"   📍 Site Detected: {result['site']}")
            print(f"   🌐 Proxy Used: {result['proxy_used']}")
            print(f"   💼 Title: {result['title']}")
            print(f"   🏢 Company: {result['company']}")
            print(f"   📍 Location: {result['location']}")
            print(f"   📄 Description Length: {len(result['description'])} characters")
            print(f"   🔐 Modal Closed: {result['modal_closed']}")
            
            if show_full_description:
                print(f"\n   📄 FULL JOB DESCRIPTION:")
                print(f"   {'-' * 60}")
                print(f"   {result['description'][:2000]}...")  # Show first 2000 chars
                print(f"   {'-' * 60}")
            else:
                print(f"   📝 Description Preview: {result['description'][:200]}...")
                
        else:
            print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
            print(f"   🌐 Proxy Used: {result['proxy_used']}")
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        
    return result if 'result' in locals() else None

async def test_all_sites_direct():
    """Test all sites with direct connection (no proxy)"""
    
    test_jobs = [
        {
            'site': 'LinkedIn',
            'url': 'https://in.linkedin.com/jobs/intern-software-development-jobs-bengaluru?position=1&pageNum=0'
        },
        {
            'site': 'Indeed', 
            'url': 'http://in.indeed.com/q-backend-developer-internship-l-remote-jobs.html?__cf_chl_tk=w0.QSiY857bACClTh8gz.KlvK0HUwTwXG.3mdFgKEsg-1752605701-1.0.1.1-9.dVWrGQFD1mdPEaKcnMxKCzh3nX6zR6g9aHMmFqzME&vjk=d6c7e3735ba837e3'
        },
        {
            'site': 'Internshala',
            'url': 'https://internshala.com/internship/detail/work-from-home-part-time-backend-development-internship-at-bug-aetherium1750326786'
        },
        {
            'site': 'Wellfound',
            'url': 'https://wellfound.com/jobs/2153913-software-engineer-backend-intern'
        }
    ]
    
    print("🚀 Testing All Job Sites with Direct Connection")
    print("=" * 80)
    
    config = get_safe_config()  # Use safe configuration
    
    successful_results = []
    
    for job in test_jobs:
        result = await test_single_site(job, config=config, show_full_description=True)
        if result and result['success']:
            successful_results.append(result)
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Successful: {len(successful_results)}/{len(test_jobs)}")
    print(f"   🌐 All requests via: Direct connection")
    
    return successful_results

async def test_all_sites_with_proxy():
    """Test all sites with proxy rotation (if proxies are configured)"""
    
    if not EXAMPLE_PROXIES:
        print("\n⚠️  No proxies configured. Add proxy URLs to EXAMPLE_PROXIES to test proxy routing.")
        return []
    
    test_jobs = [
        {
            'site': 'LinkedIn',
            'url': 'https://in.linkedin.com/jobs/intern-software-development-jobs-bengaluru?position=1&pageNum=0'
        },
        {
            'site': 'Indeed', 
            'url': 'http://in.indeed.com/q-backend-developer-internship-l-remote-jobs.html?__cf_chl_tk=w0.QSiY857bACClTh8gz.KlvK0HUwTwXG.3mdFgKEsg-1752605701-1.0.1.1-9.dVWrGQFD1mdPEaKcnMxKCzh3nX6zR6g9aHMmFqzME&vjk=d6c7e3735ba837e3'
        },
        {
            'site': 'Internshala',
            'url': 'https://internshala.com/internship/detail/work-from-home-part-time-backend-development-internship-at-bug-aetherium1750326786'
        },
        {
            'site': 'Wellfound',
            'url': 'https://wellfound.com/jobs/2153913-software-engineer-backend-intern'
        }
    ]
    
    print("\n🌐 Testing All Job Sites with Proxy Rotation")
    print("=" * 80)
    
    config = get_proxy_config(EXAMPLE_PROXIES)
    
    successful_results = []
    proxy_usage = {}
    
    for job in test_jobs:
        result = await test_single_site(job, config=config, show_full_description=False)
        if result and result['success']:
            successful_results.append(result)
            proxy = result['proxy_used']
            proxy_usage[proxy] = proxy_usage.get(proxy, 0) + 1
    
    print(f"\n📊 PROXY USAGE SUMMARY:")
    for proxy, count in proxy_usage.items():
        print(f"   🌐 {proxy}: {count} requests")
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   ✅ Successful: {len(successful_results)}/{len(test_jobs)}")
    
    return successful_results

async def batch_test_all_sites():
    """Test all sites using batch processing"""
    
    job_urls = [
        'https://in.linkedin.com/jobs/intern-software-development-jobs-bengaluru?position=1&pageNum=0',
        'http://in.indeed.com/q-backend-developer-internship-l-remote-jobs.html?__cf_chl_tk=w0.QSiY857bACClTh8gz.KlvK0HUwTwXG.3mdFgKEsg-1752605701-1.0.1.1-9.dVWrGQFD1mdPEaKcnMxKCzh3nX6zR6g9aHMmFqzME&vjk=d6c7e3735ba837e3',
        'https://internshala.com/internship/detail/work-from-home-part-time-backend-development-internship-at-bug-aetherium1750326786',
        'https://wellfound.com/jobs/2153913-software-engineer-backend-intern'
    ]
    
    print("\n📦 Testing Batch Processing")
    print("=" * 80)
    
    config = get_proxy_config(EXAMPLE_PROXIES) if EXAMPLE_PROXIES else get_safe_config()
    
    results = await scrape_multiple_jobs(job_urls, config=config)
    
    print(f"\n📊 BATCH RESULTS:")
    successful = 0
    for i, result in enumerate(results, 1):
        if result['success']:
            successful += 1
            print(f"   {i}. ✅ {result['site']}: {result['title']}")
            print(f"      🌐 Proxy: {result['proxy_used']}")
        else:
            print(f"   {i}. ❌ Failed: {result.get('error', 'Unknown')}")
            print(f"      🌐 Proxy: {result['proxy_used']}")
    
    print(f"\n📊 Batch Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    return results

async def main():
    """Main test function"""
    
    print("🔍 Multi-Site Job Scraper Test Suite")
    print("=" * 80)
    print("Testing job description extraction from:")
    print("  • LinkedIn")
    print("  • Indeed") 
    print("  • Internshala")
    print("  • Wellfound")
    print("=" * 80)
    
    # Test 1: Direct connection
    direct_results = await test_all_sites_direct()
    
    # Test 2: Proxy routing (if configured)
    if EXAMPLE_PROXIES:
        proxy_results = await test_all_sites_with_proxy()
    else:
        print(f"\n💡 To test proxy routing:")
        print(f"   1. Add your proxy URLs to EXAMPLE_PROXIES list")
        print(f"   2. Run the script again")
    
    # Test 3: Batch processing
    batch_results = await batch_test_all_sites()
    
    print(f"\n🎉 All tests completed!")
    print(f"📋 To add your own proxies, edit EXAMPLE_PROXIES list in this file")

if __name__ == "__main__":
    asyncio.run(main()) 