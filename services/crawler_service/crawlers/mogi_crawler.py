"""
Mogi.vn Crawler
Scrapes property listings from mogi.vn
"""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from services.crawler_service.crawlers.base_crawler import BaseCrawler


class MogiCrawler(BaseCrawler):
    """
    Crawler for mogi.vn
    """

    def __init__(self):
        super().__init__(
            site_name="Mogi.vn",
            base_url="https://mogi.vn"
        )

    async def get_listing_urls(self, max_pages: int) -> List[str]:
        """Get listing URLs from Mogi search results"""
        listing_urls = []

        # Search URL (apartments for sale in HCMC)
        search_url = f"{self.base_url}/mua-can-ho-chung-cu-tp-ho-chi-minh"

        async with AsyncWebCrawler(
            config=BrowserConfig(headless=True, verbose=False)
        ) as crawler:
            for page in range(1, max_pages + 1):
                try:
                    url = f"{search_url}?page={page}" if page > 1 else search_url

                    result = await crawler.arun(
                        url=url,
                        config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                    )

                    if result.success:
                        soup = BeautifulSoup(result.html, 'html.parser')

                        # Find listing links
                        links = soup.find_all('a', href=re.compile(r'^/.*\.html$'))

                        for link in links:
                            href = link.get('href')
                            if href and '.html' in href and '/mua-' not in href:
                                full_url = f"{self.base_url}{href}"
                                if full_url not in listing_urls:
                                    listing_urls.append(full_url)

                        self.logger.info(
                            f"Page {page}: Found {len(links)} listings (total: {len(listing_urls)})"
                        )

                except Exception as e:
                    self.logger.error(f"Error getting URLs from page {page}: {e}")
                    continue

        return listing_urls

    async def parse_listing(self, html: str, markdown: str) -> Optional[Dict[str, Any]]:
        """Parse a single Mogi listing"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title_elem = soup.find('h1', class_=re.compile(r'title'))
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract price
            price_elem = soup.find('div', class_=re.compile(r'price'))
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self._normalize_price(price_text) if price_text else None

            # Extract location
            location_elem = soup.find('div', class_=re.compile(r'address|location'))
            location = location_elem.get_text(strip=True) if location_elem else None

            # Parse district/ward
            district = None
            ward = None
            if location:
                district_match = re.search(r'Quận\s+([^,]+)', location)
                if district_match:
                    district = f"Quận {district_match.group(1).strip()}"

                ward_match = re.search(r'Phường\s+([^,]+)', location)
                if ward_match:
                    ward = f"Phường {ward_match.group(1).strip()}"

            # Extract specs
            specs = {}
            spec_items = soup.find_all('div', class_=re.compile(r'info|detail'))
            for item in spec_items:
                text = item.get_text(strip=True).lower()

                if 'diện tích' in text:
                    specs['area'] = self._extract_number(text)
                elif 'phòng ngủ' in text:
                    specs['bedrooms'] = int(self._extract_number(text) or 0)
                elif 'phòng tắm' in text or 'wc' in text:
                    specs['bathrooms'] = int(self._extract_number(text) or 0)
                elif 'hướng' in text:
                    specs['direction'] = text.split('hướng')[-1].strip()

            # Extract description
            description_elem = soup.find('div', class_=re.compile(r'description|content'))
            description = description_elem.get_text(strip=True) if description_elem else markdown

            # Extract amenities
            amenities = self._extract_amenities_from_text(description)

            return {
                'title': title,
                'price': price,
                'price_text': price_text,
                'location': location,
                'district': district,
                'ward': ward,
                'area': specs.get('area'),
                'bedrooms': specs.get('bedrooms'),
                'bathrooms': specs.get('bathrooms'),
                'direction': specs.get('direction'),
                'amenities': amenities,
                'description': description[:500] if description else None
            }

        except Exception as e:
            self.logger.error(f"Error parsing Mogi listing: {e}")
            return None

    def _extract_amenities_from_text(self, text: str) -> List[str]:
        """Extract amenities from description text"""
        if not text:
            return []

        text_lower = text.lower()
        amenities = []

        amenity_keywords = {
            'hồ bơi': 'swimming_pool',
            'gym': 'gym',
            'parking': 'parking',
            'thang máy': 'elevator',
            'bảo vệ': 'security_24_7',
            'sân tennis': 'tennis_court',
            'siêu thị': 'supermarket',
            'vườn': 'garden',
            'ban công': 'balcony',
            'view sông': 'river_view',
            'view biển': 'sea_view'
        }

        for keyword, amenity in amenity_keywords.items():
            if keyword in text_lower:
                if amenity not in amenities:
                    amenities.append(amenity)

        return amenities
