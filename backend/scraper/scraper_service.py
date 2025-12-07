from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

from backend.scraper.static_scraper import StaticScraper
from backend.scraper.js_scraper import JSScraper
from backend.scraper.section_parser import SectionParser
from backend.models import ScrapeResult, Meta, Section, Interactions, Error, Content, Link, Image


class ScraperService:
    def __init__(self):
        self.static_scraper = None
        self.js_scraper = None
    
    def scrape(self, url: str) -> ScrapeResult:
        errors: List[Error] = []
        strategy = "static"
        html = None
        final_url = url
        meta_data = {}
        sections_data: List[Section] = []
        interactions = Interactions()
        
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            errors.append(Error(
                message=f"Invalid URL scheme: {parsed.scheme}. Only http and https are supported.",
                phase="validation"
            ))
            return self._create_empty_result(url, errors)
        
        try:
            with StaticScraper() as static_scraper:
                result = static_scraper.fetch(url)
                if result:
                    html, final_url = result
                    meta_data = static_scraper.extract_meta(html, final_url)
                    
                    if static_scraper.is_static_sufficient(html):
                        parser = SectionParser(final_url)
                        sections_data = parser.parse(html)
                        strategy = "static"
                    else:
                        strategy = "js_fallback"
                        html = None
        except Exception as e:
            errors.append(Error(
                message=f"Static scraping failed: {str(e)}",
                phase="fetch"
            ))
            strategy = "js_fallback"
        
        if strategy == "js_fallback" or (html and len(sections_data) == 0):
            try:
                with JSScraper(headless=True) as js_scraper:
                    html, final_url, interactions_dict = js_scraper.scrape(
                        url,
                        max_depth=3,
                        enable_clicks=True,
                        enable_scroll=True
                    )
                    
                    if not meta_data:
                        with StaticScraper() as static_scraper:
                            meta_data = static_scraper.extract_meta(html, final_url)
                    
                    parser = SectionParser(final_url)
                    sections_data = parser.parse(html)
                    
                    interactions = Interactions(
                        clicks=interactions_dict.get("clicks", []),
                        scrolls=interactions_dict.get("scrolls", 0),
                        pages=interactions_dict.get("pages", [final_url])
                    )
                    
                    strategy = "js"
            except Exception as e:
                errors.append(Error(
                    message=f"JS scraping failed: {str(e)}",
                    phase="render"
                ))
                if not html and not sections_data:
                    errors.append(Error(
                        message="Both static and JS scraping failed. No content extracted.",
                        phase="parse"
                    ))
        
        if not sections_data:
            errors.append(Error(
                message="No sections could be extracted from the page.",
                phase="parse"
            ))
            sections_data = [Section(
                id="fallback-0",
                type="unknown",
                label="Content",
                sourceUrl=final_url,
                content=Content(
                    text=html[:500] if html else "No content available",
                    headings=[],
                    links=[],
                    images=[],
                    lists=[],
                    tables=[]
                ),
                rawHtml=html[:1000] if html else "",
                truncated=len(html) > 1000 if html else False
            )]
        
        meta = Meta(
            title=meta_data.get("title", ""),
            description=meta_data.get("description", ""),
            language=meta_data.get("language", "en"),
            canonical=meta_data.get("canonical")
        )
        
        result = ScrapeResult(
            url=final_url,
            scrapedAt=datetime.utcnow().isoformat() + "Z",
            meta=meta,
            sections=sections_data,
            interactions=interactions,
            errors=errors
        )
        
        return result
    
    def _create_empty_result(self, url: str, errors: List[Error]) -> ScrapeResult:
        return ScrapeResult(
            url=url,
            scrapedAt=datetime.utcnow().isoformat() + "Z",
            meta=Meta(),
            sections=[],
            interactions=Interactions(),
            errors=errors
        )

