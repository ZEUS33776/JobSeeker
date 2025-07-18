import asyncio
import logging
import sys
from typing import Optional, Dict, Any, List, Tuple
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse
import concurrent.futures
import threading

# Fix for Windows asyncio subprocess issue - set at module level
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except:
        pass  # Ignore if already set

logger = logging.getLogger(__name__)

# Windows-compatible scraper wrapper
def _run_scraper_in_thread(job_url: str, config, headless: bool = True) -> Dict[str, Any]:
    """Run scraper in a separate thread with its own event loop for Windows compatibility"""
    
    async def _scrape_in_new_loop():
        try:
            # Set up new event loop for this thread
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the scraper
            async with JobSiteScraper(headless=headless, config=config) as scraper:
                return await scraper.scrape_job_description(job_url)
        except Exception as e:
            logger.error(f"Error in threaded scraper: {e}")
            return {
                'url': job_url,
                'site': 'unknown',
                'title': None,
                'company': None,
                'location': None,
                'description': None,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
        finally:
            if 'loop' in locals():
                loop.close()
    
    # Run in separate thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, _scrape_in_new_loop())
        return future.result()

@dataclass
class ScrapingConfig:
    """Configuration for safe scraping practices"""
    min_delay: int = 5000
    max_delay: int = 15000
    requests_per_hour: int = 10
    max_daily_requests: int = 50
    rotate_user_agents: bool = True
    use_proxy: bool = False
    proxy_list: List[str] = None
    respect_robots_txt: bool = True

class RateLimiter:
    """Rate limiter to prevent overwhelming job sites"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.request_history = []
        self.daily_requests = 0
        self.last_reset = datetime.now().date()
    
    async def wait_if_needed(self):
        """Wait if we're hitting rate limits"""
        now = datetime.now()
        
        if now.date() > self.last_reset:
            self.daily_requests = 0
            self.last_reset = now.date()
            
        if self.daily_requests >= self.config.max_daily_requests:
            logger.warning(f"Daily request limit ({self.config.max_daily_requests}) reached")
            raise Exception("Daily request limit exceeded")
            
        hour_ago = now - timedelta(hours=1)
        self.request_history = [req_time for req_time in self.request_history if req_time > hour_ago]
        
        if len(self.request_history) >= self.config.requests_per_hour:
            oldest_request = min(self.request_history)
            wait_time = (oldest_request + timedelta(hours=1) - now).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
                
        delay = random.randint(self.config.min_delay, self.config.max_delay) / 1000
        await asyncio.sleep(delay)
        
        self.request_history.append(now)
        self.daily_requests += 1

class JobSiteScraper:
    """Multi-site job description scraper with anti-detection measures"""
    
    # Job site configurations
    SITE_CONFIGS = {
        'linkedin.com': {
            'name': 'LinkedIn',
            'description_selectors': [
                '.description__text--rich',
                '.description__text',
                '.jobs-description__content',
                '.show-more-less-html__markup'
            ],
            'title_selectors': [
                'h1.jobs-unified-top-card__job-title',
                'h1.topcard__title',
                '.job-details-jobs-unified-top-card__job-title h1'
            ],
            'company_selectors': [
                '.jobs-unified-top-card__company-name a',
                '.topcard__org-name-link',
                '.job-details-jobs-unified-top-card__company-name a'
            ],
            'location_selectors': [
                '.jobs-unified-top-card__bullet',
                '.topcard__flavor--bullet'
            ],
            'modal_selectors': [
                '[data-test-modal="guest-frontend-challenge-modal"] button[aria-label="Dismiss"]',
                '.modal__dismiss',
                '.artdeco-modal__dismiss',
                'button[aria-label="Dismiss"]'
            ]
        },
        'naukri.com': {
            'name': 'Naukri',
            'description_selectors': [
                'section.styles_job-desc-container_txpYf',  # Exact selector from user feedback
                '.styles_job-desc-container_txpYf',        # Class only version
                'section.styles_job-desc-container__txpYf', # Original with double underscore
                '.styles_job-desc-container__txpYf',       # Fallback version
                '.job-desc-container',
                '.jd-description',
                '[class*="job-desc"]',  # Catch any job-desc class variations
                '[class*="description"]'  # Fallback for any description class
            ],
            'title_selectors': [
                '.jd-header-title',
                '.job-title',
                'h1',
                '[class*="title"]'
            ],
            'company_selectors': [
                '.jd-header-company-name',
                '.company-name',
                '.comp-name',
                '[class*="company"]'
            ],
            'location_selectors': [
                '.jd-job-loc',
                '.job-location',
                '.location',
                '[class*="location"]'
            ],
            'modal_selectors': [
                '.modal-close',
                '.close-modal',
                'button[aria-label="Close"]'
            ],
            'dynamic_loading': True,  # Flag to indicate this site needs special handling
            'extra_wait_time': 8000,  # Extra wait time for dynamic content
            'anti_bot_protection': True,  # Note: This site blocks automated access
            'success_rate': 'low'  # Due to anti-bot measures
        },
        'wellfound.com': {
            'name': 'Wellfound',
            'description_selectors': [
                '#job-description',
                '.job-description',
                '.description-content'
            ],
            'title_selectors': [
                '.job-title',
                'h1.title',
                'h1'
            ],
            'company_selectors': [
                '.company-name',
                '.startup-name',
                '.company-link'
            ],
            'location_selectors': [
                '.job-location',
                '.location',
                '.remote-ok'
            ],
            'modal_selectors': [
                '.modal-close',
                'button[aria-label="Close"]'
            ]
        },
        'indeed.com': {
            'name': 'Indeed',
            'description_selectors': [
                '#jobDescriptionText',
                '.jobsearch-jobDescriptionText',
                '.job-description'
            ],
            'title_selectors': [
                '.jobsearch-JobInfoHeader-title',
                'h1.jobsearch-JobInfoHeader-title',
                '.job-title'
            ],
            'company_selectors': [
                '.jobsearch-InlineCompanyRating .icl-u-lg-mr--sm',
                '.company-name',
                '[data-testid="inlineHeader-companyName"]'
            ],
            'location_selectors': [
                '.jobsearch-JobInfoHeader-subtitle',
                '.job-location',
                '[data-testid="job-location"]'
            ],
            'modal_selectors': [
                '.popover-x-button',
                'button[aria-label="close"]'
            ]
        },
        'internshala.com': {
            'name': 'Internshala',
            'description_selectors': [
                '.internship_details',
                '.internship-details',
                '.job-description'
            ],
            'title_selectors': [
                '.profile',
                '.internship-title',
                'h1'
            ],
            'company_selectors': [
                '.company-name',
                '.company',
                '.org-name'
            ],
            'location_selectors': [
                '.location_link',
                '.locations',
                '.location'
            ],
            'modal_selectors': [
                '.modal-close',
                'button[aria-label="Close"]'
            ]
        }
    }
    
    def __init__(self, headless: bool = True, timeout: int = 30000, config: ScrapingConfig = None):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.config = config or ScrapingConfig()
        self.rate_limiter = RateLimiter(self.config)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Start the browser and context with anti-detection measures"""
        try:
            self.playwright = await async_playwright().start()
            
            user_agent = random.choice(self.user_agents) if self.config.rotate_user_agents else self.user_agents[0]
            
            launch_args = [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args
            )
            
            context_options = {
                'user_agent': user_agent,
                'viewport': {
                    'width': random.randint(1200, 1920),
                    'height': random.randint(800, 1080)
                },
                'device_scale_factor': random.choice([1, 1.25, 1.5]),
                'has_touch': random.choice([True, False]),
                'is_mobile': False,
                'locale': 'en-US',
                'timezone_id': 'America/New_York'
            }
            
            # Track which proxy is being used
            self.current_proxy = None
            if self.config.use_proxy and self.config.proxy_list:
                proxy = random.choice(self.config.proxy_list)
                context_options['proxy'] = {'server': proxy}
                self.current_proxy = proxy
                logger.info(f"Using proxy: {proxy}")
                
            self.context = await self.browser.new_context(**context_options)
            
            await self.context.add_init_script("""
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
            
            logger.info(f"Browser started with user agent: {user_agent[:50]}...")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
            
    async def close(self):
        """Close browser and context"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def handle_cloudflare_verification(self, page: Page) -> bool:
        """Handle Cloudflare verification and wait for completion"""
        try:
            max_attempts = 6  # Maximum wait attempts (30 seconds total)
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
                    logger.info("✅ Cloudflare verification completed or not detected")
                    return True
                    
                logger.info(f"🔄 Cloudflare verification in progress (attempt {attempt + 1}/{max_attempts})")
                await page.wait_for_timeout(5000)  # Wait 5 seconds
                attempt += 1
            
            logger.warning("⚠️ Cloudflare verification may not have completed")
            return False
            
        except Exception as e:
            logger.error(f"Error handling Cloudflare verification: {e}")
            return False

    def detect_job_site(self, url: str) -> str:
        """Detect which job site the URL belongs to"""
        domain = urlparse(url).netloc.lower()
        
        for site_key in self.SITE_CONFIGS.keys():
            if site_key in domain:
                return site_key
                
        # Default to generic selectors
        return 'generic'
    
    async def close_modals(self, page: Page, site_config: dict) -> bool:
        """Close any modals that might be open"""
        modal_closed = False
        
        try:
            await page.wait_for_timeout(2000)
            
            for selector in site_config.get('modal_selectors', []):
                try:
                    modal_button = page.locator(selector).first
                    if await modal_button.is_visible():
                        await modal_button.click()
                        await page.wait_for_timeout(1000)
                        modal_closed = True
                        logger.info(f"Closed modal using selector: {selector}")
                        break
                except:
                    continue
                    
            if not modal_closed:
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(500)
                
        except Exception as e:
            logger.warning(f"Error while closing modals: {e}")
            
        return modal_closed
    
    async def extract_text_by_selectors(self, page: Page, selectors: List[str]) -> Optional[str]:
        """Extract text using a list of selectors (first match wins)"""
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    text = await element.inner_text()
                    return text.strip() if text else None
            except:
                continue
        return None

    async def extract_text_by_selectors_with_debug(self, page: Page, selectors: List[str], element_name: str = "element") -> Tuple[Optional[str], str]:
        """Extract text using selectors with detailed debugging info"""
        debug_info = []
        
        for i, selector in enumerate(selectors):
            try:
                element = page.locator(selector).first
                
                # Check if element exists
                count = await page.locator(selector).count()
                if count == 0:
                    debug_info.append(f"Selector {i+1}: '{selector}' - Not found (0 elements)")
                    continue
                    
                debug_info.append(f"Selector {i+1}: '{selector}' - Found {count} elements")
                
                # Check if visible
                if await element.is_visible():
                    text = await element.inner_text()
                    if text and text.strip():
                        debug_info.append(f"✅ Successfully extracted {len(text)} characters using selector {i+1}")
                        return text.strip(), "; ".join(debug_info)
                    else:
                        debug_info.append(f"Selector {i+1}: Element visible but empty text")
                else:
                    debug_info.append(f"Selector {i+1}: Element found but not visible")
                    
            except Exception as e:
                debug_info.append(f"Selector {i+1}: Error - {str(e)}")
                continue
                
        return None, "; ".join(debug_info)
    
    async def scrape_job_description(self, job_url: str) -> Dict[str, Any]:
        """Scrape job description from any supported job site"""
        if not self.context:
            raise RuntimeError("Browser context not initialized. Use 'async with' or call start() first.")
            
        page = await self.context.new_page()
        
        try:
            logger.info(f"Scraping job from URL: {job_url}")
            
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed()
            
            # Detect job site and get configuration
            site_key = self.detect_job_site(job_url)
            site_config = self.SITE_CONFIGS.get(site_key, self.SITE_CONFIGS['linkedin.com'])  # Fallback
            site_name = site_config['name']
            
            logger.info(f"Detected job site: {site_name}")
            
            # Navigate to the job page
            await page.goto(job_url, wait_until='domcontentloaded', timeout=self.timeout)
            
            # Check for access denied or blocking
            page_title = await page.title()
            page_content = await page.content()
            
            access_denied_indicators = [
                'access denied',
                'blocked',
                'forbidden',
                'captcha',
                'bot detection',
                'unusual traffic'
            ]
            
            is_blocked = any(indicator in page_title.lower() for indicator in access_denied_indicators)
            is_blocked = is_blocked or any(indicator in page_content.lower() for indicator in access_denied_indicators)
            
            if is_blocked:
                logger.warning(f"Access denied or bot detection on {site_name}. Title: {page_title}")
                return {
                    'url': job_url,
                    'site': site_name,
                    'title': None,
                    'company': None,
                    'location': None,
                    'description': None,
                    'success': False,
                    'error': f'{site_name} is blocking automated access. Try accessing the job manually or use a different job board.',
                    'access_blocked': True,
                    'timestamp': time.time()
                }
            
            # Enhanced waiting for slow-loading sites
            await page.wait_for_timeout(random.randint(3000, 5000))
            
            # Handle Cloudflare verification
            cloudflare_success = await self.handle_cloudflare_verification(page)
            if not cloudflare_success:
                logger.warning("Proceeding despite potential Cloudflare issues")
            
            # Close any modals
            modal_closed = await self.close_modals(page, site_config)
            
            # Scroll to load content and wait for dynamic loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await page.wait_for_timeout(3000)
            
            # Additional scroll to trigger lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Wait for JavaScript content to fully render (especially for SPAs like Wellfound)
            try:
                await page.wait_for_load_state('networkidle', timeout=8000)
                logger.info("Network idle - JavaScript content loaded")
            except:
                logger.info("Network didn't become idle, proceeding with extraction")
                await page.wait_for_timeout(3000)  # Additional wait
            
            # Special handling for sites with dynamic loading (like Naukri)
            if site_config.get('dynamic_loading', False):
                extra_wait = site_config.get('extra_wait_time', 5000)
                logger.info(f"Dynamic loading site detected, waiting additional {extra_wait}ms for {site_name}")
                await page.wait_for_timeout(extra_wait)
                
                # Additional scroll and wait for Naukri to ensure content loads
                if 'naukri' in site_key:
                    logger.info("Performing Naukri-specific loading sequence...")
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await page.wait_for_timeout(2000)
                    
                    # Try to wait for the specific Naukri description container
                    try:
                        await page.wait_for_selector('.styles_job-desc-container__txpYf, section.styles_job-desc-container__txpYf', timeout=5000)
                        logger.info("Naukri description container loaded successfully")
                    except:
                        logger.warning("Naukri description container not found within timeout, proceeding anyway")
            
            # Extract job information using site-specific selectors
            description, desc_debug = await self.extract_text_by_selectors_with_debug(page, site_config['description_selectors'], "description")
            title = await self.extract_text_by_selectors(page, site_config['title_selectors'])
            company = await self.extract_text_by_selectors(page, site_config['company_selectors'])
            location = await self.extract_text_by_selectors(page, site_config['location_selectors'])
            
            # Determine success and error message
            success = description is not None
            error_msg = None if success else f"Description extraction failed: {desc_debug}"
            
            result = {
                'url': job_url,
                'site': site_name,
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'modal_closed': modal_closed,
                'success': success,
                'error': error_msg,
                'proxy_used': self.current_proxy or 'Direct connection',
                'timestamp': time.time()
            }
            
            if description:
                logger.info(f"Successfully scraped {site_name} job: {title} ({len(description)} chars)")
            else:
                logger.warning(f"Failed to extract description from {site_name}: {desc_debug}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping job: {e}")
            return {
                'url': job_url,
                'site': 'unknown',
                'title': None,
                'company': None,
                'location': None,
                'description': None,
                'modal_closed': False,
                'success': False,
                'error': str(e),
                'proxy_used': getattr(self, 'current_proxy', None) or 'Direct connection',
                'timestamp': time.time()
            }
        finally:
            await page.close()

# Production-ready configurations
def get_safe_config() -> ScrapingConfig:
    """Conservative configuration for safe scraping"""
    return ScrapingConfig(
        min_delay=8000,
        max_delay=15000,
        requests_per_hour=5,
        max_daily_requests=20,
        rotate_user_agents=True,
        use_proxy=False
    )

def get_production_config() -> ScrapingConfig:
    """Production configuration optimized for reliability"""
    return ScrapingConfig(
        min_delay=6000,
        max_delay=12000,
        requests_per_hour=8,
        max_daily_requests=40,
        rotate_user_agents=True,
        use_proxy=False
    )

def get_proxy_config(proxy_list: List[str]) -> ScrapingConfig:
    """Configuration for proxy-enabled scraping"""
    return ScrapingConfig(
        min_delay=5000,
        max_delay=10000,
        requests_per_hour=15,
        max_daily_requests=60,
        rotate_user_agents=True,
        use_proxy=True,
        proxy_list=proxy_list
    )

# Convenience functions
async def scrape_job(job_url: str, config: ScrapingConfig = None, headless: bool = True) -> Dict[str, Any]:
    """Scrape a single job from any supported site - Windows compatible"""
    config = config or get_safe_config()
    
    # Use threaded approach on Windows to avoid asyncio subprocess issues
    if sys.platform == 'win32':
        try:
            # Run in thread to avoid Windows asyncio issues
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                _run_scraper_in_thread, 
                job_url, 
                config, 
                headless
            )
            return result
        except Exception as e:
            logger.error(f"Error in Windows-compatible scraper: {e}")
            return {
                'url': job_url,
                'site': 'unknown',
                'title': None,
                'company': None,
                'location': None,
                'description': None,
                'success': False,
                'error': f"Windows scraper error: {str(e)}",
                'timestamp': time.time()
            }
    else:
        # Use regular async approach on non-Windows
        async with JobSiteScraper(headless=headless, config=config) as scraper:
            return await scraper.scrape_job_description(job_url)

async def scrape_multiple_jobs(job_urls: List[str], config: ScrapingConfig = None) -> List[Dict[str, Any]]:
    """Scrape multiple jobs with rate limiting"""
    config = config or get_safe_config()
    results = []
    
    async with JobSiteScraper(headless=True, config=config) as scraper:
        for i, url in enumerate(job_urls, 1):
            logger.info(f"Processing job {i}/{len(job_urls)}")
            try:
                result = await scraper.scrape_job_description(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to scrape job {i}: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                })
                
    return results

