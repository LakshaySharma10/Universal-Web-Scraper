from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import time


class JSScraper:
    def __init__(self, timeout: int = 30000, headless: bool = True):
        self.timeout = timeout
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def start(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        if not self.context:
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        if not self.page:
            self.page = self.context.new_page()
    
    def scrape(
        self, 
        url: str, 
        max_depth: int = 3,
        enable_clicks: bool = True,
        enable_scroll: bool = True
    ) -> Tuple[str, str, Dict]:
        if not self.page:
            self.start()
        
        interactions = {
            "clicks": [],
            "scrolls": 0,
            "pages": [url]
        }
        
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
            
            self.page.goto(url, wait_until="networkidle", timeout=self.timeout)
            final_url = self.page.url
            interactions["pages"][0] = final_url
            
            self._wait_for_content()
            
            if enable_clicks:
                self._perform_clicks(interactions)
            
            if enable_scroll:
                self._perform_scrolls(interactions, max_depth)
            
            html = self.page.content()
            return html, final_url, interactions
            
        except Exception as e:
            print(f"JS scrape error: {e}")
            html = self.page.content() if self.page else ""
            final_url = url
            return html, final_url, interactions
    
    def _wait_for_content(self):
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        
        try:
            selectors = ["main", "article", "body", "[role='main']"]
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=2000)
                    break
                except:
                    continue
        except:
            pass
        
        time.sleep(1)
    
    def _perform_clicks(self, interactions: Dict):
        tab_selectors = [
            '[role="tab"]',
            '[role="tablist"] [role="tab"]',
            '.tab',
            '[class*="tab"]',
            'button[aria-controls]'
        ]
        
        for selector in tab_selectors:
            try:
                tabs = self.page.query_selector_all(selector)
                for i, tab in enumerate(tabs[:3]):
                    if tab.is_visible():
                        tab.click(timeout=2000)
                        interactions["clicks"].append(f"{selector}[{i}]")
                        time.sleep(1)
                        break
            except:
                continue
        
        load_more_selectors = [
            'button:has-text("Load more")',
            'button:has-text("Show more")',
            'button:has-text("See more")',
            '[class*="load-more"]',
            '[class*="show-more"]',
            '[id*="load-more"]',
            '[id*="show-more"]'
        ]
        
        for selector in load_more_selectors:
            try:
                buttons = self.page.query_selector_all(selector)
                for button in buttons[:2]:
                    if button.is_visible():
                        button.click(timeout=2000)
                        interactions["clicks"].append(selector)
                        time.sleep(2)
            except:
                continue
    
    def _perform_scrolls(self, interactions: Dict, max_depth: int = 3):
        scroll_count = 0
        last_height = 0
        same_height_count = 0
        
        while scroll_count < max_depth:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            interactions["scrolls"] += 1
            scroll_count += 1
            
            time.sleep(2)
            
            current_height = self.page.evaluate("document.body.scrollHeight")
            if current_height == last_height:
                same_height_count += 1
                if same_height_count >= 2:
                    break
            else:
                same_height_count = 0
                last_height = current_height
            
            next_links = self.page.query_selector_all('a:has-text("Next"), a:has-text("next"), [rel="next"]')
            if next_links:
                try:
                    next_link = next_links[0]
                    if next_link.is_visible():
                        href = next_link.get_attribute("href")
                        if href:
                            next_url = urljoin(self.page.url, href)
                            if next_url not in interactions["pages"] and len(interactions["pages"]) < max_depth:
                                interactions["clicks"].append(f'a[href="{href}"]')
                                next_link.click(timeout=3000)
                                interactions["pages"].append(next_url)
                                time.sleep(2)
                                scroll_count = 0
                                continue
                except:
                    pass
    
    def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                self.page.close()
        except:
            pass
        try:
            if self.context:
                self.context.close()
        except:
            pass
        try:
            if self.browser:
                self.browser.close()
        except:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except:
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

