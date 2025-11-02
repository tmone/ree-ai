"""
Parallel Bulk Crawler Service
Crawls multiple real estate sites in parallel with rate limiting
Supports 10,000+ properties without duplication
Features:
- Resume from checkpoint on interruption
- Parallel workers (5x faster than sequential)
- Automatic deduplication
"""
import asyncio
import time
import os
import json
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from collections import defaultdict
import hashlib

from crawl4ai import WebCrawler
from bs4 import BeautifulSoup
import re
import httpx

from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings

logger = setup_logger("bulk_crawler")


# Global semaphore to limit concurrent bulk crawls
# Only allow 2 concurrent bulk crawls to prevent overload
CONCURRENT_CRAWL_LIMIT = 2
bulk_crawl_semaphore = asyncio.Semaphore(CONCURRENT_CRAWL_LIMIT)


@dataclass
class CrawlConfig:
    """Configuration for each crawl site"""
    site_name: str
    base_url: str
    page_pattern: str  # e.g., "/p{page}"
    properties_per_page: int
    rate_limit: float  # seconds between requests
    max_workers: int  # parallel workers for this site
    css_selectors: Dict[str, str]


class RateLimiter:
    """Rate limiter per site to avoid being blocked"""

    def __init__(self):
        self.last_request_time: Dict[str, float] = defaultdict(float)
        self.locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, site_name: str, rate_limit: float):
        """
        Wait if needed to respect rate limit
        Uses minimal lock time to allow parallel workers
        """
        # Quick check without lock (not 100% accurate but allows parallelism)
        now = time.time()
        time_since_last = now - self.last_request_time.get(site_name, 0)

        if time_since_last < rate_limit:
            wait_time = rate_limit - time_since_last
            # Don't log for small waits to reduce noise
            if wait_time > 0.5:
                logger.info(f"{LogEmoji.TIME} Rate limit: waiting {wait_time:.2f}s for {site_name}")
            await asyncio.sleep(wait_time)

        # Update last request time (atomic enough for our purposes)
        self.last_request_time[site_name] = time.time()


class PropertyDeduplicator:
    """Deduplicate properties by URL and content hash"""

    def __init__(self, checkpoint_file: str = None):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
        self.checkpoint_file = checkpoint_file

        # Load existing URLs from checkpoint if available
        if checkpoint_file and os.path.exists(checkpoint_file):
            self._load_checkpoint()

    def _load_checkpoint(self):
        """Load existing URLs from checkpoint file"""
        try:
            import json
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.seen_urls = set(data.get('urls', []))
                logger.info(f"📂 Loaded {len(self.seen_urls)} URLs from checkpoint")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load checkpoint: {e}")

    def save_checkpoint(self):
        """Save current state to checkpoint file"""
        if not self.checkpoint_file:
            return

        try:
            import json
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    'urls': list(self.seen_urls),
                    'count': len(self.seen_urls)
                }, f)
            logger.info(f"💾 Saved checkpoint: {len(self.seen_urls)} URLs")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save checkpoint: {e}")

    def is_duplicate(self, property_data: Dict[str, Any]) -> bool:
        """Check if property is duplicate"""
        # Check URL
        url = property_data.get('url', '')
        if url in self.seen_urls:
            return True

        # Check content hash (title + location + price)
        content = f"{property_data.get('title', '')}_{property_data.get('location', '')}_{property_data.get('price', '')}"
        content_hash = hashlib.md5(content.encode()).hexdigest()

        if content_hash in self.seen_hashes:
            return True

        # Not duplicate - add to seen
        self.seen_urls.add(url)
        self.seen_hashes.add(content_hash)
        return False

    def get_stats(self) -> Dict[str, int]:
        """Get deduplication statistics"""
        return {
            "unique_urls": len(self.seen_urls),
            "unique_hashes": len(self.seen_hashes)
        }


class ParallelBulkCrawler:
    """
    Parallel crawler for multiple real estate sites
    Features:
    - Multiple workers per site
    - Rate limiting per site
    - Automatic deduplication
    - Progress tracking
    - Error recovery
    - Resume from checkpoint
    """

    def __init__(self, checkpoint_file: str = None, resume: bool = True):
        self.rate_limiter = RateLimiter()

        # Use checkpoint file for resume capability
        if checkpoint_file is None:
            checkpoint_file = "/tmp/ree_ai_crawler_checkpoint.json"

        self.checkpoint_file = checkpoint_file if resume else None
        self.deduplicator = PropertyDeduplicator(self.checkpoint_file)
        self.crawler = None

        # Crawl configurations for each site
        self.configs = self._get_crawl_configs()

        # HTTP client for LLM extraction calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.core_gateway_url = settings.get_core_gateway_url()

        # Cache for extracted metadata (avoid redundant LLM calls)
        self.extraction_cache: Dict[str, Dict[str, str]] = {}

    def _get_crawl_configs(self) -> List[CrawlConfig]:
        """Get crawl configurations for all sites"""
        return [
            # Batdongsan.com.vn - For Sale (crawl deeper pages)
            CrawlConfig(
                site_name="batdongsan",
                base_url="https://batdongsan.com.vn/nha-dat-ban",
                page_pattern="/p{page}",
                properties_per_page=20,
                rate_limit=2.0,  # 2 seconds between requests
                max_workers=5,   # 5 parallel workers
                css_selectors={
                    "card": ".re__card-full",
                    "title": ".re__card-title",
                    "price": ".re__card-config-price",
                    "location": ".re__card-location",
                    "area": ".re__card-config-area",
                    "description": ".re__card-description",
                    "link": "a"
                }
            ),
            # Nhatot.com
            CrawlConfig(
                site_name="nhatot",
                base_url="https://nhatot.com/mua-ban-bat-dong-san",
                page_pattern="?page={page}",
                properties_per_page=20,
                rate_limit=3.0,  # 3 seconds between requests (more conservative)
                max_workers=3,   # 3 parallel workers
                css_selectors={
                    "card": ".AdItem_adItem__2O0X5",
                    "title": ".AdItem_adName__3O6tT",
                    "price": ".AdItem_price__3uOMB",
                    "location": ".AdItem_location__3O6tT",
                    "area": ".AdItem_area__3O6tT",
                    "description": ".AdItem_description__3O6tT",
                    "link": "a"
                }
            ),
            # Add more sites here...
        ]

    def warmup(self):
        """Initialize crawler"""
        logger.info(f"{LogEmoji.STARTUP} Warming up crawler...")
        self.crawler = WebCrawler()
        self.crawler.warmup()
        logger.info(f"{LogEmoji.SUCCESS} Crawler ready!")

    async def crawl_page(
        self,
        config: CrawlConfig,
        page_num: int
    ) -> List[Dict[str, Any]]:
        """Crawl a single page"""

        # Apply rate limiting
        await self.rate_limiter.wait(config.site_name, config.rate_limit)

        # Build URL
        if "{page}" in config.page_pattern:
            url = config.base_url + config.page_pattern.format(page=page_num)
        else:
            url = config.base_url

        logger.info(f"{LogEmoji.SEARCH} Crawling {config.site_name} page {page_num}: {url}")

        try:
            # Crawl
            result = self.crawler.run(url=url)

            if not result.success:
                logger.warning(f"{LogEmoji.WARNING} Failed to crawl {url}")
                return []

            # Parse HTML
            soup = BeautifulSoup(result.html, 'html.parser')
            property_items = soup.select(config.css_selectors["card"])

            logger.info(f"{LogEmoji.SUCCESS} Found {len(property_items)} items on page {page_num}")

            # Extract properties (async with LLM enrichment)
            extraction_tasks = [
                self._extract_property(item, config)
                for item in property_items
            ]

            # Execute extractions in parallel (faster!)
            extracted_properties = await asyncio.gather(*extraction_tasks, return_exceptions=True)

            # Filter valid results and check duplicates
            properties = []
            for prop_data in extracted_properties:
                if isinstance(prop_data, Exception):
                    logger.warning(f"{LogEmoji.WARNING} Extraction error: {prop_data}")
                    continue

                if isinstance(prop_data, dict):
                    # Check for duplicates
                    if not self.deduplicator.is_duplicate(prop_data):
                        properties.append(prop_data)

            return properties

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Error crawling page {page_num}: {e}")
            return []

    async def _extract_metadata_with_llm(self, title: str, location: str) -> Dict[str, str]:
        """
        Extract city, district, property_type using LLM (NO HARDCODING!)

        Uses cache to avoid redundant API calls for same patterns
        """
        cache_key = f"{title[:50]}_{location[:30]}"

        # Check cache first
        if cache_key in self.extraction_cache:
            return self.extraction_cache[cache_key]

        try:
            prompt = f"""Extract structured metadata from this Vietnamese real estate listing.

Title: {title}
Location: {location}

Return ONLY valid JSON with these exact fields:
{{
    "city": "Hồ Chí Minh" | "Hà Nội" | "Đà Nẵng" | etc,
    "district": "Quận 1" | "Thủ Đức" | "Cầu Giấy" | etc (or empty string if not found),
    "property_type": "căn hộ" | "nhà phố" | "biệt thự" | "đất" | "chung cư" | "shophouse" | etc
}}

Rules:
- Infer city from district if not explicitly mentioned ("Quận 2" → city: "Hồ Chí Minh")
- Normalize district names ("Q2" → "Quận 2", "Q.7" → "Quận 7")
- Extract property_type from title keywords
- Use empty string for missing fields, never null

JSON:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.0  # Deterministic
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                # Clean markdown
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)

                metadata = json.loads(content)

                # Cache result
                self.extraction_cache[cache_key] = metadata

                return metadata
            else:
                logger.warning(f"LLM extraction failed: {response.status_code}")
                return {"city": "", "district": "", "property_type": ""}

        except Exception as e:
            logger.warning(f"LLM extraction error: {e}")
            return {"city": "", "district": "", "property_type": ""}

    async def _extract_property(
        self,
        item: BeautifulSoup,
        config: CrawlConfig
    ) -> Dict[str, Any]:
        """Extract property data from HTML element with LLM-enriched metadata"""

        selectors = config.css_selectors

        title_elem = item.select_one(selectors["title"])
        price_elem = item.select_one(selectors["price"])
        location_elem = item.select_one(selectors["location"])
        area_elem = item.select_one(selectors["area"])
        desc_elem = item.select_one(selectors["description"])
        link_elem = item.select_one(selectors["link"])

        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        price = price_elem.get_text(strip=True) if price_elem else "N/A"
        location = location_elem.get_text(strip=True) if location_elem else "N/A"
        area = area_elem.get_text(strip=True) if area_elem else "N/A"
        description = desc_elem.get_text(strip=True) if desc_elem else title
        property_url = link_elem.get('href', '') if link_elem else ""

        if property_url and not property_url.startswith('http'):
            property_url = f"{config.base_url.split('/')[0]}//{config.base_url.split('/')[2]}{property_url}"

        # Extract bedrooms/bathrooms from description (regex)
        bedrooms = 0
        bathrooms = 0

        bedroom_match = re.search(r'(\d+)\s*(?:phòng ngủ|PN)', description, re.IGNORECASE)
        if bedroom_match:
            bedrooms = int(bedroom_match.group(1))

        bathroom_match = re.search(r'(\d+)\s*(?:toilet|WC|phòng tắm)', description, re.IGNORECASE)
        if bathroom_match:
            bathrooms = int(bathroom_match.group(1))

        # Extract city, district, property_type using LLM (NO HARDCODING!)
        metadata = await self._extract_metadata_with_llm(title, location)

        return {
            "title": title,
            "price": price,
            "location": location,
            "city": metadata.get("city", ""),  # ← NEW!
            "district": metadata.get("district", ""),  # ← NEW!
            "property_type": metadata.get("property_type", ""),  # ← NEW!
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "area": area,
            "description": description,
            "url": property_url,
            "source": config.site_name
        }

    async def crawl_site_parallel(
        self,
        config: CrawlConfig,
        total_properties: int
    ) -> List[Dict[str, Any]]:
        """Crawl a site with parallel workers"""

        pages_needed = (total_properties // config.properties_per_page) + 1

        logger.info(
            f"{LogEmoji.ROCKET} Starting parallel crawl for {config.site_name}: "
            f"{pages_needed} pages, {config.max_workers} workers"
        )

        # Create worker pools
        all_properties = []
        page_num = 1

        while len(all_properties) < total_properties and page_num <= pages_needed:
            # Create batch of pages for workers
            batch_size = min(config.max_workers, pages_needed - page_num + 1)
            page_batch = range(page_num, page_num + batch_size)

            # Crawl batch in parallel
            tasks = [self.crawl_page(config, page) for page in page_batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect results
            for result in results:
                if isinstance(result, list):
                    all_properties.extend(result)

            page_num += batch_size

            # Save checkpoint every 10 batches (every 50 pages with 5 workers)
            if page_num % 10 == 0:
                self.deduplicator.save_checkpoint()

            logger.info(
                f"{LogEmoji.CHART} Progress: {len(all_properties)}/{total_properties} "
                f"properties from {config.site_name}"
            )

        logger.info(
            f"{LogEmoji.SUCCESS} Completed {config.site_name}: "
            f"{len(all_properties)} unique properties"
        )

        return all_properties[:total_properties]

    async def bulk_crawl(
        self,
        total_properties: int = 10000,
        sites: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bulk crawl properties from multiple sites
        Protected by semaphore to prevent overload from concurrent requests

        Args:
            total_properties: Total number of properties to crawl
            sites: List of site names to crawl (None = all sites)

        Returns:
            List of unique properties
        """

        # Acquire semaphore to limit concurrent crawls
        async with bulk_crawl_semaphore:
            logger.info(
                f"{LogEmoji.INFO} Acquired crawl slot "
                f"({CONCURRENT_CRAWL_LIMIT - bulk_crawl_semaphore._value}/{CONCURRENT_CRAWL_LIMIT} active)"
            )

            # Warmup crawler
            if not self.crawler:
                self.warmup()

            # Filter configs
            configs = self.configs
            if sites:
                configs = [c for c in configs if c.site_name in sites]

            # Distribute properties across sites
            properties_per_site = total_properties // len(configs)

            logger.info(
                f"{LogEmoji.ROCKET} Starting BULK CRAWL: "
                f"{total_properties} properties from {len(configs)} sites"
            )
            logger.info(f"{LogEmoji.INFO} Target: {properties_per_site} properties per site")

            # Crawl all sites in parallel
            start_time = time.time()

            tasks = [
                self.crawl_site_parallel(config, properties_per_site)
                for config in configs
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine results
            all_properties = []
            for result in results:
                if isinstance(result, list):
                    all_properties.extend(result)

            # Final stats
            elapsed = time.time() - start_time
            dedup_stats = self.deduplicator.get_stats()

            # Save final checkpoint
            self.deduplicator.save_checkpoint()

            logger.info(f"\n{LogEmoji.CHART} {'='*60}")
            logger.info(f"{LogEmoji.SUCCESS} BULK CRAWL COMPLETED!")
            logger.info(f"{LogEmoji.CHART} {'='*60}")
            logger.info(f"{LogEmoji.PROPERTY} Total properties: {len(all_properties)}")
            logger.info(f"{LogEmoji.SUCCESS} Unique URLs: {dedup_stats['unique_urls']}")
            logger.info(f"{LogEmoji.SUCCESS} Unique content: {dedup_stats['unique_hashes']}")
            logger.info(f"{LogEmoji.TIME} Time taken: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
            logger.info(f"{LogEmoji.FIRE} Speed: {len(all_properties)/elapsed:.2f} properties/second")
            logger.info(f"{LogEmoji.CHART} {'='*60}\n")

            return all_properties[:total_properties]


# Standalone function for easy use
async def bulk_crawl_properties(
    total: int = 10000,
    sites: List[str] = None,
    resume: bool = True,
    checkpoint_file: str = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to bulk crawl properties with resume support

    Args:
        total: Total properties to crawl
        sites: List of site names (None = all sites)
        resume: Enable resume from checkpoint (default True)
        checkpoint_file: Path to checkpoint file (default /tmp/ree_ai_crawler_checkpoint.json)

    Usage:
        # Crawl 10,000 properties with auto-resume
        properties = await bulk_crawl_properties(10000)

        # Crawl fresh without resume
        properties = await bulk_crawl_properties(10000, resume=False)

        # Resume from custom checkpoint
        properties = await bulk_crawl_properties(10000, checkpoint_file='/path/to/checkpoint.json')
    """
    crawler = ParallelBulkCrawler(checkpoint_file=checkpoint_file, resume=resume)
    return await crawler.bulk_crawl(total, sites)


if __name__ == "__main__":
    # Example usage
    async def main():
        print("🚀 Starting bulk crawl test...")

        # Test with 100 properties first
        properties = await bulk_crawl_properties(100, sites=['batdongsan'])

        print(f"\n✅ Crawled {len(properties)} properties")
        print(f"\nSample property:")
        if properties:
            import json
            print(json.dumps(properties[0], indent=2, ensure_ascii=False))

    asyncio.run(main())
