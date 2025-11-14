"""
Base Crawler Class
Abstract base for site-specific crawlers
"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from shared.utils.logger import logger, LogEmoji


class BaseCrawler(ABC):
    """
    Abstract base class for real estate site crawlers

    Subclasses must implement:
    - parse_listing(): Extract data from a single listing
    - get_listing_urls(): Get URLs of listings to scrape
    """

    def __init__(self, site_name: str, base_url: str):
        """
        Args:
            site_name: Human-readable site name
            base_url: Base URL of the site
        """
        self.site_name = site_name
        self.base_url = base_url
        self.logger = logger

    async def crawl(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Crawl listings from the site

        Args:
            max_pages: Maximum number of listing pages to crawl

        Returns:
            List of parsed listings
        """
        self.logger.info(
            f"{LogEmoji.TARGET} Starting crawl: {self.site_name} (max_pages={max_pages})"
        )

        try:
            # Get listing URLs
            listing_urls = await self.get_listing_urls(max_pages)
            self.logger.info(
                f"{LogEmoji.INFO} Found {len(listing_urls)} listings to scrape"
            )

            # Crawl each listing
            listings = []
            async with AsyncWebCrawler(
                config=BrowserConfig(
                    headless=True,
                    verbose=False
                )
            ) as crawler:
                for i, url in enumerate(listing_urls[:max_pages * 10], 1):  # Limit total
                    try:
                        result = await crawler.arun(
                            url=url,
                            config=CrawlerRunConfig(
                                cache_mode=CacheMode.BYPASS,
                                wait_for_images=False,
                                word_count_threshold=50
                            )
                        )

                        if result.success:
                            listing_data = await self.parse_listing(result.html, result.markdown)
                            if listing_data:
                                listing_data['source_url'] = url
                                listing_data['source_site'] = self.site_name
                                listings.append(listing_data)

                                self.logger.info(
                                    f"{LogEmoji.SUCCESS} [{i}/{len(listing_urls)}] Scraped: {listing_data.get('title', 'Unknown')[:50]}"
                                )
                        else:
                            self.logger.warning(
                                f"{LogEmoji.WARNING} [{i}] Failed to crawl: {url}"
                            )

                        # Rate limiting
                        await asyncio.sleep(1)

                    except Exception as e:
                        self.logger.error(f"{LogEmoji.ERROR} Error crawling {url}: {e}")
                        continue

            self.logger.info(
                f"{LogEmoji.SUCCESS} Crawl complete: {len(listings)} listings scraped"
            )
            return listings

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Crawl failed: {e}")
            return []

    @abstractmethod
    async def get_listing_urls(self, max_pages: int) -> List[str]:
        """
        Get URLs of property listings to scrape

        Args:
            max_pages: Maximum number of listing pages to crawl

        Returns:
            List of listing URLs
        """
        pass

    @abstractmethod
    async def parse_listing(self, html: str, markdown: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single property listing

        Args:
            html: Raw HTML content
            markdown: Markdown-converted content (from Crawl4AI)

        Returns:
            Parsed listing data or None if parsing failed
        """
        pass

    def _extract_number(self, text: str) -> Optional[float]:
        """Extract first number from text"""
        import re
        if not text:
            return None
        match = re.search(r'[\d,\.]+', text)
        if match:
            return float(match.group().replace(',', ''))
        return None

    def _normalize_price(self, price_text: str) -> Optional[float]:
        """
        Normalize price to VND

        Examples:
        - "5.5 tỷ" → 5500000000
        - "25 triệu/tháng" → 25000000
        - "3,5 tỷ" → 3500000000
        """
        if not price_text:
            return None

        price_text = price_text.lower().strip()

        # Extract number
        import re
        match = re.search(r'([\d,\.]+)', price_text)
        if not match:
            return None

        number = float(match.group().replace(',', '.'))

        # Check unit
        if 'tỷ' in price_text or 'ty' in price_text or 'billion' in price_text:
            return number * 1_000_000_000
        elif 'triệu' in price_text or 'million' in price_text:
            return number * 1_000_000
        elif 'nghìn' in price_text or 'nghin' in price_text or 'thousand' in price_text:
            return number * 1_000
        else:
            # Assume already in VND
            return number
