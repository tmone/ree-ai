"""
Batdongsan.com.vn Crawler
Scrapes property listings from batdongsan.com.vn
"""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from services.crawler_service.crawlers.base_crawler import BaseCrawler


class BatdongsanCrawler(BaseCrawler):
    """
    Crawler for batdongsan.com.vn

    Extracts:
    - Property type
    - Location (district, ward, street)
    - Price
    - Area
    - Bedrooms, bathrooms
    - Amenities and features
    - Description
    """

    def __init__(self):
        super().__init__(
            site_name="Batdongsan.com.vn",
            base_url="https://batdongsan.com.vn"
        )

    async def get_listing_urls(self, max_pages: int) -> List[str]:
        """
        Get listing URLs from search results

        Args:
            max_pages: Number of search result pages to crawl

        Returns:
            List of listing URLs
        """
        listing_urls = []

        # Search URL (apartments for sale in HCMC)
        search_url = f"{self.base_url}/ban-can-ho-chung-cu-tp-hcm"

        async with AsyncWebCrawler(
            config=BrowserConfig(headless=True, verbose=False)
        ) as crawler:
            for page in range(1, max_pages + 1):
                try:
                    url = f"{search_url}/p{page}" if page > 1 else search_url

                    result = await crawler.arun(
                        url=url,
                        config=CrawlerRunConfig(
                            cache_mode=CacheMode.BYPASS,
                            wait_for_images=False
                        )
                    )

                    if result.success:
                        soup = BeautifulSoup(result.html, 'html.parser')

                        # Find listing links
                        # Pattern: <a href="/..."> with class containing "js__product-link-for-product-id"
                        links = soup.find_all('a', href=re.compile(r'^/.*-pr\d+'))

                        for link in links:
                            href = link.get('href')
                            if href and '-pr' in href:  # Listing URLs contain -prXXXXX
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
        """
        Parse a single Batdongsan listing

        Args:
            html: Raw HTML
            markdown: Markdown content

        Returns:
            Parsed listing data
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title_elem = soup.find('h1', class_=re.compile(r'title|name'))
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract price
            price_elem = soup.find('span', class_=re.compile(r'price'))
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self._normalize_price(price_text) if price_text else None

            # Extract location
            location_elem = soup.find('div', class_=re.compile(r'location|address'))
            location = location_elem.get_text(strip=True) if location_elem else None

            # Parse location into district/ward
            district = None
            ward = None
            if location:
                # Pattern: "..., Phường X, Quận Y, ..."
                district_match = re.search(r'Quận\s+([^,]+)', location)
                if district_match:
                    district = f"Quận {district_match.group(1).strip()}"

                ward_match = re.search(r'Phường\s+([^,]+)', location)
                if ward_match:
                    ward = f"Phường {ward_match.group(1).strip()}"

            # Extract specifications
            specs = {}
            spec_items = soup.find_all('div', class_=re.compile(r'spec|characteristic'))
            for item in spec_items:
                label_elem = item.find('span', class_=re.compile(r'label|title'))
                value_elem = item.find('span', class_=re.compile(r'value|content'))

                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True).lower()
                    value = value_elem.get_text(strip=True)

                    if 'diện tích' in label or 'area' in label:
                        specs['area'] = self._extract_number(value)
                    elif 'phòng ngủ' in label or 'bedroom' in label:
                        specs['bedrooms'] = int(self._extract_number(value) or 0)
                    elif 'phòng tắm' in label or 'toilet' in label or 'bathroom' in label:
                        specs['bathrooms'] = int(self._extract_number(value) or 0)
                    elif 'hướng' in label or 'direction' in label:
                        specs['direction'] = value
                    elif 'nội thất' in label or 'furniture' in label:
                        specs['furniture'] = value

            # Extract amenities from description
            description_elem = soup.find('div', class_=re.compile(r'description|detail'))
            description = description_elem.get_text(strip=True) if description_elem else markdown

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
                'furniture': specs.get('furniture'),
                'amenities': amenities,
                'description': description[:500] if description else None,  # Truncate
                'raw_specs': specs
            }

        except Exception as e:
            self.logger.error(f"Error parsing Batdongsan listing: {e}")
            return None

    def _extract_amenities_from_text(self, text: str) -> List[str]:
        """
        Extract amenities mentioned in description text

        Args:
            text: Property description

        Returns:
            List of amenities found
        """
        if not text:
            return []

        text_lower = text.lower()
        amenities = []

        # Common amenities keywords
        amenity_keywords = {
            'hồ bơi': 'swimming_pool',
            'bể bơi': 'swimming_pool',
            'pool': 'swimming_pool',
            'gym': 'gym',
            'phòng gym': 'gym',
            'fitness': 'gym',
            'bãi đỗ xe': 'parking',
            'parking': 'parking',
            'chỗ đậu xe': 'parking',
            'thang máy': 'elevator',
            'elevator': 'elevator',
            'lift': 'elevator',
            'bảo vệ 24/7': 'security_24_7',
            'security': 'security_24_7',
            'an ninh': 'security_24_7',
            'sân tennis': 'tennis_court',
            'tennis': 'tennis_court',
            'siêu thị': 'supermarket',
            'supermarket': 'supermarket',
            'khu vui chơi': 'playground',
            'playground': 'playground',
            'vườn': 'garden',
            'garden': 'garden',
            'ban công': 'balcony',
            'balcony': 'balcony',
            'sân thượng': 'rooftop_terrace',
            'rooftop': 'rooftop_terrace',
            'view sông': 'river_view',
            'view biển': 'sea_view',
            'view thành phố': 'city_view'
        }

        for keyword, amenity in amenity_keywords.items():
            if keyword in text_lower:
                if amenity not in amenities:
                    amenities.append(amenity)

        return amenities
