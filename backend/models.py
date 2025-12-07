from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal
from datetime import datetime


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL to scrape (must be http or https)")


class Meta(BaseModel):
    title: str = ""
    description: str = ""
    language: str = "en"
    canonical: Optional[str] = None


class Link(BaseModel):
    text: str
    href: str


class Image(BaseModel):
    src: str
    alt: str = ""


class Content(BaseModel):
    headings: List[str] = []
    text: str = ""
    links: List[Link] = []
    images: List[Image] = []
    lists: List[List[str]] = []
    tables: List[dict] = []


class Section(BaseModel):
    id: str
    type: Literal["hero", "section", "nav", "footer", "list", "grid", "faq", "pricing", "unknown"]
    label: str
    sourceUrl: str
    content: Content
    rawHtml: str
    truncated: bool


class Error(BaseModel):
    message: str
    phase: str


class Interactions(BaseModel):
    clicks: List[str] = []
    scrolls: int = 0
    pages: List[str] = []


class ScrapeResult(BaseModel):
    url: str
    scrapedAt: str
    meta: Meta
    sections: List[Section]
    interactions: Interactions
    errors: List[Error] = []


class ScrapeResponse(BaseModel):
    result: ScrapeResult

