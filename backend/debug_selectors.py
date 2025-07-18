#!/usr/bin/env python3
"""
HTML Structure Inspector for Job Sites
Helps debug and find correct CSS selectors for Indeed and Wellfound
"""

import asyncio
import logging
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def inspect_page_structure(url: str, site_name: str):
    """Inspect HTML structure to find job description elements"""
    
    print(f"\n🔍 Inspecting {site_name}")
    print("=" * 60)
    print(f"URL: {url}")
    print("-" * 60)
    
    async with async_playwright() as p:
        # Use same configuration as main scraper
        browser = await p.chromium.launch(
            headless=False,  # Open visible browser to see what's happening
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Add anti-detection script
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Handle Cloudflare verification
            print("⏳ Checking for Cloudflare verification...")
            print("💡 If you see a verification challenge, you can complete it manually in the browser")
            
            max_attempts = 10  # 50 seconds total
            attempt = 0
            
            while attempt < max_attempts:
                page_title = await page.title()
                page_content = await page.content()
                
                # Check for Cloudflare indicators
                cloudflare_indicators = [
                    'just a moment',
                    'please wait', 
                    'checking your browser',
                    'cloudflare',
                    'ray id',
                    'cf-browser-verification'
                ]
                
                is_cloudflare = any(indicator in page_title.lower() for indicator in cloudflare_indicators)
                is_cloudflare = is_cloudflare or any(indicator in page_content.lower() for indicator in cloudflare_indicators)
                
                if not is_cloudflare:
                    print("✅ Page loaded successfully!")
                    break
                    
                print(f"🔄 Cloudflare verification detected (attempt {attempt + 1}/{max_attempts})")
                await page.wait_for_timeout(5000)  # Wait 5 seconds
                attempt += 1
            
            if attempt >= max_attempts:
                print("⚠️ Cloudflare verification may not have completed, proceeding anyway...")
            
            # Wait for JavaScript content to load (especially for Wellfound)
            print("⏳ Waiting for JavaScript content to render...")
            await page.wait_for_timeout(8000)  # Wait 8 seconds for JS
            
            # Try to wait for network to be idle (no pending requests)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
                print("🌐 Network idle - content should be loaded")
            except:
                print("⚠️ Network didn't become idle, proceeding anyway")
            
            # Get final page title
            title = await page.title()
            print(f"📄 Final Page Title: {title}")
            
            # Check for common job description containers
            selectors_to_check = [
                # Indeed selectors
                '#jobDescriptionText',
                '.jobsearch-jobDescriptionText', 
                '.job-description',
                '[data-testid="jobsearch-JobComponent-description"]',
                '.jobsearch-JobComponent-description',
                
                # Wellfound selectors  
                '#job-description',
                '.job-description',
                '.description-content',
                '[data-test="JobDescription"]',
                '.job-details',
                
                # Generic containers that might contain descriptions
                '.description',
                '[class*="description"]',
                '[id*="description"]',
                '.content',
                '.details',
                'main',
                'article'
            ]
            
            found_elements = []
            
            for selector in selectors_to_check:
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        element = page.locator(selector).first
                        if await element.is_visible():
                            text = await element.inner_text()
                            if text and len(text) > 50:  # Meaningful content
                                found_elements.append({
                                    'selector': selector,
                                    'count': count,
                                    'text_length': len(text),
                                    'preview': text[:200] + "..." if len(text) > 200 else text
                                })
                except:
                    continue
            
            if found_elements:
                print(f"\n✅ Found {len(found_elements)} potential description containers:")
                for i, elem in enumerate(found_elements, 1):
                    print(f"\n{i}. Selector: '{elem['selector']}'")
                    print(f"   Elements: {elem['count']}")
                    print(f"   Text Length: {elem['text_length']} characters")
                    print(f"   Preview: {elem['preview']}")
            else:
                print("❌ No job description containers found!")
                
                # Let's check what's actually on the page
                print("\n🔍 Checking page content...")
                body_text = await page.locator('body').inner_text()
                print(f"📄 Total page text: {len(body_text)} characters")
                
                if len(body_text) > 0:
                    print(f"📝 Page preview: {body_text[:500]}...")
                else:
                    # If no text, check HTML structure
                    print("🔍 No text found, checking HTML structure...")
                    html_content = await page.content()
                    print(f"📄 HTML length: {len(html_content)} characters")
                    
                    # Check for common elements
                    div_count = await page.locator('div').count()
                    span_count = await page.locator('span').count()
                    p_count = await page.locator('p').count()
                    print(f"📊 Elements found: {div_count} divs, {span_count} spans, {p_count} paragraphs")
                    
                    # Check for login/auth requirements
                    login_indicators = ['login', 'sign in', 'authenticate', 'unauthorized', 'access denied']
                    for indicator in login_indicators:
                        if indicator in html_content.lower():
                            print(f"🔒 Possible authentication required: found '{indicator}'")
                            break
                    
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"debug_{site_name.lower()}_screenshot.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    except:
                        print("📸 Could not save screenshot")
                
                # Check for error messages or redirects
                if 'error' in title.lower() or (len(body_text) > 0 and 'not found' in body_text.lower()):
                    print("⚠️  Possible error page or redirect detected")
                    
        except Exception as e:
            print(f"❌ Error inspecting page: {e}")
            
        finally:
            await browser.close()

async def main():
    """Inspect problematic job sites"""
    
    test_urls = [
        {
            'site': 'Indeed',
            'url': 'http://in.indeed.com/q-backend-developer-internship-l-remote-jobs.html?__cf_chl_tk=w0.QSiY857bACClTh8gz.KlvK0HUwTwXG.3mdFgKEsg-1752605701-1.0.1.1-9.dVWrGQFD1mdPEaKcnMxKCzh3nX6zR6g9aHMmFqzME&vjk=d6c7e3735ba837e3'
        },
        {
            'site': 'Wellfound', 
            'url': 'https://wellfound.com/jobs/2153913-software-engineer-backend-intern'
        }
    ]
    
    print("🔧 HTML Structure Inspector for Job Sites")
    print("=" * 80)
    
    for job_info in test_urls:
        await inspect_page_structure(job_info['url'], job_info['site'])
        print("\n" + "=" * 80)
    
    print("\n🎉 Inspection complete!")
    print("💡 Use the found selectors to update SITE_CONFIGS in scraper.py")

if __name__ == "__main__":
    asyncio.run(main()) 