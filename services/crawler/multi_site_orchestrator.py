"""
Multi-Site Crawler Orchestrator
Manages crawling across multiple real estate sites simultaneously
Features:
- Load configs from database
- Parallel multi-site crawling
- Adaptive rate limiting
- Error detection and recovery
- Incremental vs full crawl modes
"""
import asyncio
import time
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

from crawl4ai import WebCrawler
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

from shared.utils.logger import setup_logger, LogEmoji

logger = setup_logger("orchestrator")


class SiteStatus(str, Enum):
    """Status of a crawl site"""
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    FAILED = "failed"
    DISABLED = "disabled"


class CrawlMode(str, Enum):
    """Crawl mode"""
    FULL = "full"  # Crawl all pages
    INCREMENTAL = "incremental"  # Only crawl new listings


@dataclass
class CrawlConfig:
    """Configuration for a site (loaded from DB)"""
    id: int
    site_domain: str
    site_name: str
    base_url: str
    selectors: Dict[str, str]
    pagination: Dict[str, Any]
    rate_limit_seconds: float
    max_workers: int
    crawl_frequency: str
    enabled: bool
    status: str
    quality_score: float
    data_fields: List[str]


class RateLimitDetector:
    """Detects rate limiting and adapts crawl speed"""

    # Error patterns for different rate limit types
    PATTERNS = {
        "http_429": [429],
        "cloudflare_challenge": ["Checking your browser", "Just a moment", "Enable JavaScript and cookies"],
        "captcha": ["recaptcha", "hcaptcha"],
        "ip_block": ["Access Denied", "Forbidden", "403 Forbidden", "blocked your access", "banned"],
        "too_fast": ["slow down", "too many requests within"],
    }

    @classmethod
    def detect(cls, status_code: int, html: str, headers: Dict[str, str]) -> Optional[str]:
        """
        Detect if response indicates rate limiting

        IMPORTANT: Only detect ACTUAL blocking, not just presence of anti-bot code

        Returns:
            Rate limit type if detected, None otherwise
        """
        # Check HTTP status
        if status_code in cls.PATTERNS["http_429"]:
            return "http_429"

        # If status code is 403, definitely blocked
        if status_code == 403:
            return "ip_block"

        html_lower = html.lower()

        # Check if page is mostly empty (< 1000 chars = likely blocked)
        if len(html) < 1000:
            return "ip_block"

        # Check HTML content patterns (ONLY strict patterns)
        for pattern_type, patterns in cls.PATTERNS.items():
            if pattern_type == "http_429":
                continue

            for pattern in patterns:
                if isinstance(pattern, str) and pattern.lower() in html_lower:
                    # Additional validation: check if page has actual content
                    # If page has > 10KB content, it's likely not blocked
                    if len(html) > 10000:
                        # This is just Cloudflare being present, not blocking
                        continue
                    return pattern_type

        return None

    @classmethod
    def get_retry_after(cls, headers: Dict[str, str], default: int = 60) -> int:
        """Extract Retry-After from headers"""
        retry_after = headers.get('Retry-After', headers.get('retry-after'))
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return default


class MultiSiteOrchestrator:
    """
    Orchestrates crawling across multiple sites
    Features:
    - Multi-site parallel crawling
    - Adaptive rate limiting
    - Error detection and recovery
    - Incremental crawling
    - State tracking
    """

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.crawler = None
        self.running_jobs: Dict[str, asyncio.Task] = {}

        # Global semaphore to limit total concurrent sites
        self.global_semaphore = asyncio.Semaphore(5)  # Max 5 sites at once

    def warmup(self):
        """Initialize crawler"""
        if not self.crawler:
            logger.info(f"{LogEmoji.STARTUP} Warming up Multi-Site Orchestrator...")
            self.crawler = WebCrawler()
            self.crawler.warmup()
            logger.info(f"{LogEmoji.SUCCESS} Orchestrator ready!")

    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    async def load_configs(self, enabled_only: bool = True) -> List[CrawlConfig]:
        """Load crawl configurations from database"""
        logger.info(f"{LogEmoji.DATABASE} Loading site configs from database...")

        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM crawl_configs"
        if enabled_only:
            query += " WHERE enabled = true AND status IN ('active', 'rate_limited')"
        query += " ORDER BY quality_score DESC"

        cursor.execute(query)
        rows = cursor.fetchall()

        configs = []
        for row in rows:
            config = CrawlConfig(
                id=row['id'],
                site_domain=row['site_domain'],
                site_name=row['site_name'],
                base_url=row['base_url'],
                selectors=row['selectors'],
                pagination=row['pagination'],
                rate_limit_seconds=row['rate_limit_seconds'],
                max_workers=row['max_workers'],
                crawl_frequency=row['crawl_frequency'],
                enabled=row['enabled'],
                status=row['status'],
                quality_score=row['quality_score'],
                data_fields=row['data_fields']
            )
            configs.append(config)

        cursor.close()
        conn.close()

        logger.info(f"{LogEmoji.SUCCESS} Loaded {len(configs)} site configs")
        return configs

    async def start_all(self, mode: CrawlMode = CrawlMode.INCREMENTAL):
        """
        Start crawling all enabled sites

        Args:
            mode: FULL or INCREMENTAL crawl
        """
        logger.info(f"{LogEmoji.ROCKET} Starting Multi-Site Orchestrator in {mode} mode")

        if not self.crawler:
            self.warmup()

        # Load configs
        configs = await self.load_configs(enabled_only=True)

        if not configs:
            logger.warning(f"{LogEmoji.WARNING} No enabled sites found in database")
            return

        # Start crawl for each site
        logger.info(f"{LogEmoji.INFO} Starting crawl for {len(configs)} sites...")

        tasks = []
        for config in configs:
            task = asyncio.create_task(
                self.crawl_site(config, mode)
            )
            self.running_jobs[config.site_domain] = task
            tasks.append(task)

        # Wait for all crawls to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        succeeded = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - succeeded

        logger.info(f"\n{LogEmoji.CHART} {'='*60}")
        logger.info(f"{LogEmoji.SUCCESS} MULTI-SITE CRAWL COMPLETED")
        logger.info(f"{LogEmoji.CHART} {'='*60}")
        logger.info(f"{LogEmoji.SUCCESS} Succeeded: {succeeded}/{len(results)} sites")
        if failed > 0:
            logger.info(f"{LogEmoji.ERROR} Failed: {failed}/{len(results)} sites")
        logger.info(f"{LogEmoji.CHART} {'='*60}\n")

    async def crawl_site(
        self,
        config: CrawlConfig,
        mode: CrawlMode
    ) -> Dict[str, Any]:
        """
        Crawl a single site with adaptive rate limiting

        Args:
            config: Site configuration
            mode: FULL or INCREMENTAL

        Returns:
            Crawl statistics
        """
        # Ensure crawler is initialized
        if not self.crawler:
            self.warmup()

        # Acquire global semaphore (limit total concurrent sites)
        async with self.global_semaphore:
            logger.info(
                f"{LogEmoji.INFO} [{config.site_name}] Starting {mode} crawl"
            )

            # Create crawl job in database
            job_id = await self._create_job(config.site_domain, mode)

            start_time = time.time()
            stats = {
                "pages_crawled": 0,
                "properties_found": 0,
                "properties_new": 0,
                "properties_updated": 0,
                "errors": 0,
            }

            try:
                # Determine pages to crawl
                if mode == CrawlMode.FULL:
                    pages_needed = config.pagination['max_pages']
                else:
                    # Incremental: only first 5-10 pages (new listings)
                    pages_needed = min(10, config.pagination['max_pages'])

                # Crawl with parallel workers
                all_properties = []
                page_num = 1
                consecutive_errors = 0

                while page_num <= pages_needed:
                    # Create batch for workers
                    batch_size = min(config.max_workers, pages_needed - page_num + 1)
                    page_batch = range(page_num, page_num + batch_size)

                    # Crawl batch in parallel
                    tasks = [
                        self._crawl_page(config, page, stats)
                        for page in page_batch
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Collect results
                    for result in results:
                        if isinstance(result, Exception):
                            stats["errors"] += 1
                            consecutive_errors += 1
                            logger.error(f"{LogEmoji.ERROR} [{config.site_name}] Error: {result}")

                            # Too many errors? Stop crawling
                            if consecutive_errors >= 5:
                                logger.warning(
                                    f"{LogEmoji.WARNING} [{config.site_name}] "
                                    f"Too many consecutive errors, stopping"
                                )
                                await self._update_site_status(
                                    config.site_domain,
                                    SiteStatus.FAILED,
                                    str(result)
                                )
                                break
                        elif isinstance(result, list):
                            all_properties.extend(result)
                            consecutive_errors = 0  # Reset on success
                        elif result == "rate_limited":
                            logger.warning(
                                f"{LogEmoji.WARNING} [{config.site_name}] Rate limited, slowing down"
                            )
                            await asyncio.sleep(config.rate_limit_seconds * 2)
                            consecutive_errors = 0

                    page_num += batch_size
                    stats["pages_crawled"] = page_num - 1

                    logger.info(
                        f"{LogEmoji.CHART} [{config.site_name}] "
                        f"Progress: {stats['pages_crawled']}/{pages_needed} pages, "
                        f"{len(all_properties)} properties"
                    )

                # Save properties to database
                saved_stats = await self._save_properties(
                    config, all_properties, mode
                )
                stats.update(saved_stats)

                # Update job as completed
                duration = time.time() - start_time
                await self._complete_job(job_id, stats, duration)

                # Update last crawl timestamp
                await self._update_last_crawl(config.site_domain, mode)

                logger.info(
                    f"{LogEmoji.SUCCESS} [{config.site_name}] Crawl completed: "
                    f"{stats['properties_found']} total, "
                    f"{stats['properties_new']} new, "
                    f"{stats['properties_updated']} updated, "
                    f"{duration:.1f}s"
                )

                return stats

            except Exception as e:
                logger.error(f"{LogEmoji.ERROR} [{config.site_name}] Fatal error: {e}")
                stats["errors"] += 1

                # Update job as failed
                duration = time.time() - start_time
                await self._fail_job(job_id, str(e), stats, duration)

                # Update site status
                await self._update_site_status(config.site_domain, SiteStatus.FAILED, str(e))

                raise

    async def _crawl_page(
        self,
        config: CrawlConfig,
        page_num: int,
        stats: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Crawl a single page with rate limit detection

        Args:
            config: Site configuration
            page_num: Page number to crawl
            stats: Statistics dict to update

        Returns:
            List of properties or "rate_limited" if rate limited
        """
        # Apply rate limiting
        await asyncio.sleep(config.rate_limit_seconds)

        # Build URL
        pattern = config.pagination['pattern']
        if '{page}' in pattern:
            url = config.base_url.rstrip('/') + pattern.format(page=page_num)
        else:
            url = config.base_url

        logger.debug(f"{LogEmoji.SEARCH} [{config.site_name}] Crawling page {page_num}: {url}")

        try:
            # Crawl
            result = self.crawler.run(url=url)

            if not result.success:
                logger.warning(f"{LogEmoji.WARNING} [{config.site_name}] Failed to crawl {url}")
                return []

            # Detect rate limiting
            rate_limit_type = RateLimitDetector.detect(
                result.status_code if hasattr(result, 'status_code') else 200,
                result.html,
                getattr(result, 'headers', {})
            )

            if rate_limit_type:
                logger.warning(
                    f"{LogEmoji.WARNING} [{config.site_name}] "
                    f"Rate limit detected: {rate_limit_type}"
                )

                # Log rate limit event
                await self._log_rate_limit(config.site_domain, rate_limit_type, url)

                # Update site status
                await self._update_site_status(
                    config.site_domain,
                    SiteStatus.RATE_LIMITED,
                    f"Rate limit: {rate_limit_type}"
                )

                return "rate_limited"

            # Parse HTML
            soup = BeautifulSoup(result.html, 'html.parser')
            property_items = soup.select(config.selectors['card'])

            logger.debug(
                f"{LogEmoji.SUCCESS} [{config.site_name}] "
                f"Found {len(property_items)} items on page {page_num}"
            )

            # Extract properties
            properties = []
            for item in property_items:
                try:
                    prop_data = self._extract_property(item, config)
                    properties.append(prop_data)
                except Exception as e:
                    logger.warning(
                        f"{LogEmoji.WARNING} [{config.site_name}] "
                        f"Error extracting property: {e}"
                    )
                    continue

            return properties

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} [{config.site_name}] Error crawling page {page_num}: {e}")
            raise

    def _extract_property(
        self,
        item: BeautifulSoup,
        config: CrawlConfig
    ) -> Dict[str, Any]:
        """Extract property data from HTML element"""

        selectors = config.selectors

        # Extract all fields
        title_elem = item.select_one(selectors.get('title', ''))
        price_elem = item.select_one(selectors.get('price', ''))
        location_elem = item.select_one(selectors.get('location', ''))
        area_elem = item.select_one(selectors.get('area', ''))
        desc_elem = item.select_one(selectors.get('description', ''))
        link_elem = item.select_one(selectors.get('link', 'a'))

        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        price = price_elem.get_text(strip=True) if price_elem else "N/A"
        location = location_elem.get_text(strip=True) if location_elem else "N/A"
        area = area_elem.get_text(strip=True) if area_elem else "N/A"
        description = desc_elem.get_text(strip=True) if desc_elem else title
        property_url = link_elem.get('href', '') if link_elem else ""

        # Fix relative URLs
        if property_url and not property_url.startswith('http'):
            from urllib.parse import urlparse
            parsed = urlparse(config.base_url)
            property_url = f"{parsed.scheme}://{parsed.netloc}{property_url}"

        return {
            "title": title,
            "price": price,
            "location": location,
            "area": area,
            "description": description,
            "url": property_url,
            "source": config.site_domain
        }

    async def _save_properties(
        self,
        config: CrawlConfig,
        properties: List[Dict[str, Any]],
        mode: CrawlMode
    ) -> Dict[str, int]:
        """
        Save properties to database with incremental state tracking

        Returns:
            Statistics: new, updated counts
        """
        if not properties:
            return {"properties_new": 0, "properties_updated": 0}

        conn = self.get_db_connection()
        cursor = conn.cursor()

        stats = {"properties_new": 0, "properties_updated": 0}

        for prop in properties:
            url = prop.get('url', '')
            if not url:
                continue

            # Calculate content hash
            content = f"{prop.get('title')}_{prop.get('price')}_{prop.get('location')}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            url_hash = hashlib.md5(url.encode()).hexdigest()

            # Check if URL exists in crawl_state
            cursor.execute(
                "SELECT id, content_hash, property_id FROM crawl_state WHERE site_domain = %s AND url_hash = %s",
                (config.site_domain, url_hash)
            )
            existing = cursor.fetchone()

            if existing:
                # URL exists
                state_id, old_content_hash, property_id = existing

                if content_hash != old_content_hash:
                    # Content changed - update property
                    if property_id:
                        cursor.execute(
                            """
                            UPDATE properties
                            SET title = %s, price = %s, location = %s, area = %s,
                                description = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                            """,
                            (prop['title'], prop['price'], prop['location'],
                             prop['area'], prop['description'], property_id)
                        )

                    # Update state
                    cursor.execute(
                        """
                        UPDATE crawl_state
                        SET content_hash = %s, last_seen = CURRENT_TIMESTAMP,
                            last_updated = CURRENT_TIMESTAMP, status = 'updated'
                        WHERE id = %s
                        """,
                        (content_hash, state_id)
                    )
                    stats['properties_updated'] += 1
                else:
                    # No change - just update last_seen
                    cursor.execute(
                        "UPDATE crawl_state SET last_seen = CURRENT_TIMESTAMP WHERE id = %s",
                        (state_id,)
                    )
            else:
                # New URL - insert property with ON CONFLICT handling
                cursor.execute(
                    """
                    INSERT INTO properties
                    (title, price, location, area, description, url, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        price = EXCLUDED.price,
                        location = EXCLUDED.location,
                        area = EXCLUDED.area,
                        description = EXCLUDED.description,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    (prop['title'], prop['price'], prop['location'], prop['area'],
                     prop['description'], url, config.site_domain)
                )
                property_id = cursor.fetchone()[0]

                # Insert into crawl_state with ON CONFLICT handling
                cursor.execute(
                    """
                    INSERT INTO crawl_state
                    (site_domain, url, url_hash, content_hash, property_id, status)
                    VALUES (%s, %s, %s, %s, %s, 'active')
                    ON CONFLICT (site_domain, url_hash) DO UPDATE SET
                        content_hash = EXCLUDED.content_hash,
                        last_seen = CURRENT_TIMESTAMP,
                        property_id = EXCLUDED.property_id
                    """,
                    (config.site_domain, url, url_hash, content_hash, property_id)
                )
                stats['properties_new'] += 1

        conn.commit()
        cursor.close()
        conn.close()

        return stats

    async def _create_job(self, site_domain: str, job_type: str) -> int:
        """Create crawl job record"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO crawl_jobs (site_domain, job_type, status, started_at)
            VALUES (%s, %s, 'running', CURRENT_TIMESTAMP)
            RETURNING id
            """,
            (site_domain, job_type)
        )
        job_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return job_id

    async def _complete_job(self, job_id: int, stats: Dict[str, int], duration: float):
        """Mark job as completed"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE crawl_jobs
            SET status = 'completed',
                pages_crawled = %s,
                properties_found = %s,
                properties_new = %s,
                properties_updated = %s,
                errors_count = %s,
                duration_seconds = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (stats.get('pages_crawled', 0), stats.get('properties_found', 0),
             stats.get('properties_new', 0), stats.get('properties_updated', 0),
             stats.get('errors', 0), duration, job_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

    async def _fail_job(self, job_id: int, error: str, stats: Dict[str, int], duration: float):
        """Mark job as failed"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE crawl_jobs
            SET status = 'failed',
                pages_crawled = %s,
                errors_count = %s,
                duration_seconds = %s,
                error_message = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (stats.get('pages_crawled', 0), stats.get('errors', 0), duration, error, job_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

    async def _update_site_status(self, site_domain: str, status: SiteStatus, notes: str = ""):
        """Update site status"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE crawl_configs
            SET status = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE site_domain = %s
            """,
            (status, notes, site_domain)
        )

        conn.commit()
        cursor.close()
        conn.close()

    async def _update_last_crawl(self, site_domain: str, mode: CrawlMode):
        """Update last crawl timestamp"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        if mode == CrawlMode.FULL:
            field = "last_full_crawl"
        else:
            field = "last_incremental_crawl"

        cursor.execute(
            f"""
            UPDATE crawl_configs
            SET {field} = CURRENT_TIMESTAMP
            WHERE site_domain = %s
            """,
            (site_domain,)
        )

        conn.commit()
        cursor.close()
        conn.close()

    async def _log_rate_limit(self, site_domain: str, event_type: str, url: str):
        """Log rate limit event"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO rate_limit_events (site_domain, event_type, url)
            VALUES (%s, %s, %s)
            """,
            (site_domain, event_type, url)
        )

        conn.commit()
        cursor.close()
        conn.close()


# CLI for testing
async def main():
    """Test orchestrator"""
    import os

    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'ree_ai'),
        'user': os.getenv('POSTGRES_USER', 'ree_ai_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')
    }

    orchestrator = MultiSiteOrchestrator(db_config)

    # Start incremental crawl for all enabled sites
    await orchestrator.start_all(mode=CrawlMode.INCREMENTAL)


if __name__ == "__main__":
    asyncio.run(main())
