from fastapi import APIRouter, HTTPException
from backend.models import ScrapeRequest, ScrapeResponse
from backend.scraper.scraper_service import ScraperService
from concurrent.futures import ThreadPoolExecutor
import asyncio

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=2)


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest):
    try:
        loop = asyncio.get_event_loop()
        service = ScraperService()
        result = await loop.run_in_executor(executor, service.scrape, request.url)
        return ScrapeResponse(result=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )

