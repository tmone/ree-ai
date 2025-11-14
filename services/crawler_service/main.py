"""
Crawler Service - Real Estate Data Collection
Scrapes property listings from Vietnamese real estate websites
"""
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.base_service import BaseService
from services.crawler_service.crawlers.batdongsan_crawler import BatdongsanCrawler
from services.crawler_service.crawlers.mogi_crawler import MogiCrawler
from services.crawler_service.master_data_populator import MasterDataPopulator
from shared.utils.logger import LogEmoji
from shared.config import settings


class CrawlRequest(BaseModel):
    """Request to crawl a specific site"""
    site: str  # 'batdongsan', 'mogi', 'all'
    max_pages: int = 5
    extract_master_data: bool = True
    auto_populate: bool = False  # Auto-add to pending_master_data


class CrawlResponse(BaseModel):
    """Response from crawling"""
    site: str
    listings_scraped: int
    new_attributes_found: int
    processing_time_ms: float
    sample_listings: List[Dict[str, Any]]


class CrawlerService(BaseService):
    """
    Crawler Service for Real Estate Data Collection

    Capabilities:
    - Scrape listings from multiple Vietnamese real estate sites
    - Extract property attributes
    - Discover new master data (amenities, features, etc.)
    - Auto-populate pending_master_data for admin review
    """

    def __init__(self):
        super().__init__(
            name="crawler_service",
            version="1.0.0",
            capabilities=["web_scraping", "data_collection", "master_data_discovery"],
            port=8080
        )

        # Initialize crawlers
        self.crawlers = {
            'batdongsan': BatdongsanCrawler(),
            'mogi': MogiCrawler()
        }

        # Initialize master data populator
        self.populator = MasterDataPopulator()

        self.logger.info(f"{LogEmoji.SUCCESS} Crawler service initialized")
        self.logger.info(f"{LogEmoji.INFO} Available crawlers: {list(self.crawlers.keys())}")

    def setup_routes(self):
        """Setup API routes"""

        @self.app.post("/crawl", response_model=CrawlResponse)
        async def crawl_site(request: CrawlRequest):
            """
            Crawl real estate listings from specified site

            **Parameters**:
            - site: 'batdongsan', 'mogi', or 'all'
            - max_pages: Maximum pages to crawl (default: 5)
            - extract_master_data: Extract new attributes for master data
            - auto_populate: Automatically add to pending_master_data

            **Returns**:
            - Number of listings scraped
            - New attributes discovered
            - Sample listings
            """
            try:
                import time
                start_time = time.time()

                self.logger.info(
                    f"{LogEmoji.TARGET} Crawl request: site={request.site}, "
                    f"max_pages={request.max_pages}"
                )

                # Select crawler(s)
                if request.site == 'all':
                    crawlers_to_run = list(self.crawlers.values())
                elif request.site in self.crawlers:
                    crawlers_to_run = [self.crawlers[request.site]]
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unknown site: {request.site}. Available: {list(self.crawlers.keys())}"
                    )

                # Crawl
                all_listings = []
                for crawler in crawlers_to_run:
                    listings = await crawler.crawl(max_pages=request.max_pages)
                    all_listings.extend(listings)
                    self.logger.info(
                        f"{LogEmoji.SUCCESS} Scraped {len(listings)} listings from {crawler.site_name}"
                    )

                # Extract master data
                new_attributes = []
                if request.extract_master_data:
                    new_attributes = await self.populator.extract_new_attributes(all_listings)
                    self.logger.info(
                        f"{LogEmoji.AI} Discovered {len(new_attributes)} new attributes"
                    )

                # Auto-populate pending_master_data
                if request.auto_populate and new_attributes:
                    populated_count = await self.populator.populate_pending_master_data(
                        new_attributes
                    )
                    self.logger.info(
                        f"{LogEmoji.SUCCESS} Populated {populated_count} items to pending_master_data"
                    )

                processing_time = (time.time() - start_time) * 1000

                return CrawlResponse(
                    site=request.site,
                    listings_scraped=len(all_listings),
                    new_attributes_found=len(new_attributes),
                    processing_time_ms=processing_time,
                    sample_listings=all_listings[:5]  # Return first 5 as sample
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Crawl failed: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/crawlers")
        async def list_crawlers():
            """Get list of available crawlers"""
            return {
                "crawlers": [
                    {
                        "id": crawler_id,
                        "name": crawler.site_name,
                        "url": crawler.base_url
                    }
                    for crawler_id, crawler in self.crawlers.items()
                ]
            }

        @self.app.post("/schedule-crawl")
        async def schedule_periodic_crawl(
            site: str = 'all',
            interval_hours: int = 24,
            max_pages: int = 10
        ):
            """
            Schedule periodic crawling

            **Parameters**:
            - site: Which site(s) to crawl
            - interval_hours: Crawl every N hours (default: 24)
            - max_pages: Max pages per crawl

            **Returns**:
            - Schedule confirmation
            """
            # TODO: Implement with APScheduler or Celery
            return {
                "message": "Scheduled crawling (not yet implemented)",
                "site": site,
                "interval_hours": interval_hours
            }

    async def on_startup(self):
        """Initialize on startup"""
        await super().on_startup()
        await self.populator.initialize()

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.populator.close()
        await super().on_shutdown()


# Create service instance
service = CrawlerService()
app = service.app

if __name__ == "__main__":
    service.run()
