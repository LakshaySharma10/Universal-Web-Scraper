import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict


class StaticScraper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
    
    def fetch(self, url: str) -> Optional[tuple[str, str]]:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return None
            
            response = self.client.get(url)
            response.raise_for_status()
            return (response.text, str(response.url))
        except Exception as e:
            print(f"Static fetch error: {e}")
            return None
    
    def extract_meta(self, html: str, base_url: str) -> Dict:
        tree = HTMLParser(html)
        meta = {
            "title": "",
            "description": "",
            "language": "en",
            "canonical": None
        }
        
        title_tag = tree.css_first("title")
        if title_tag:
            meta["title"] = title_tag.text().strip()
        
        if not meta["title"]:
            og_title = tree.css_first('meta[property="og:title"]')
            if og_title:
                meta["title"] = og_title.attributes.get("content", "").strip()
        
        desc_tag = tree.css_first('meta[name="description"]')
        if desc_tag:
            meta["description"] = desc_tag.attributes.get("content", "").strip()
        
        if not meta["description"]:
            og_desc = tree.css_first('meta[property="og:description"]')
            if og_desc:
                meta["description"] = og_desc.attributes.get("content", "").strip()
        
        html_tag = tree.css_first("html")
        if html_tag:
            lang = html_tag.attributes.get("lang", "en")
            meta["language"] = lang.split("-")[0] if lang else "en"
        
        canonical_tag = tree.css_first('link[rel="canonical"]')
        if canonical_tag:
            canonical_href = canonical_tag.attributes.get("href", "")
            if canonical_href:
                meta["canonical"] = urljoin(base_url, canonical_href)
        
        return meta
    
    def is_static_sufficient(self, html: str) -> bool:
        tree = HTMLParser(html)
        
        scripts = tree.css("script")
        has_react = any("react" in script.text().lower() or "react" in script.attributes.get("src", "").lower() 
                       for script in scripts if script.text() or script.attributes.get("src"))
        has_vue = any("vue" in script.text().lower() or "vue" in script.attributes.get("src", "").lower() 
                     for script in scripts if script.text() or script.attributes.get("src"))
        has_angular = any("angular" in script.text().lower() or "angular" in script.attributes.get("src", "").lower() 
                         for script in scripts if script.text() or script.attributes.get("src"))
        
        main_content = tree.css_first("main, article, [role='main']")
        has_main = main_content is not None
        
        body = tree.css_first("body")
        text_length = len(body.text()) if body else 0
        
        if (has_react or has_vue or has_angular) and text_length < 500:
            return False
        
        if text_length > 1000:
            return True
        
        return True
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

