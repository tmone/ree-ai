"""
AI-Powered Site Analyzer
Automatically analyzes real estate websites to extract structure and generate crawl configs
Uses GPT-4 to understand HTML patterns and suggest optimal crawling strategies
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib

from crawl4ai import WebCrawler
from bs4 import BeautifulSoup
import httpx

from shared.utils.logger import setup_logger, LogEmoji
from shared.models.core_gateway import LLMRequest, Message, ModelType

logger = setup_logger("site_analyzer")


@dataclass
class SiteAnalysis:
    """Results from analyzing a real estate site"""
    site_domain: str
    site_name: str
    base_url: str

    # Structure analysis (required)
    property_card_selector: str
    title_selector: str
    price_selector: str
    location_selector: str
    link_selector: str

    # Pagination
    pagination_pattern: str  # e.g., "/p{page}", "?page={page}"
    max_pages_estimate: int
    properties_per_page: int

    # Data fields available
    data_fields: List[str]  # ['price', 'location', 'bedrooms', 'area', etc.]

    # Rate limiting
    rate_limit_seconds: float
    max_workers: int
    has_cloudflare: bool
    requires_js: bool

    # Quality assessment
    quality_score: float  # 1-10
    data_completeness: float  # 0-1 (percentage of fields filled)
    recommended_frequency: str  # 'hourly', 'daily', 'weekly'

    # Metadata
    analyzed_at: datetime
    analysis_confidence: float  # 0-1
    notes: str

    # Optional fields (must be at end with defaults)
    area_selector: str = ""
    description_selector: str = ""
    image_selector: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['analyzed_at'] = self.analyzed_at.isoformat()
        return data


class SiteAnalyzer:
    """
    AI-powered analyzer that understands real estate site structure
    Uses LLM to extract patterns and generate optimal configs
    """

    def __init__(self, openai_api_key: str = None):
        self.crawler = None
        self.openai_api_key = openai_api_key or self._get_api_key()

    def _get_api_key(self) -> str:
        """Get OpenAI API key from environment"""
        import os
        return os.getenv('OPENAI_API_KEY')

    def warmup(self):
        """Initialize crawler"""
        if not self.crawler:
            logger.info(f"{LogEmoji.STARTUP} Warming up Site Analyzer...")
            self.crawler = WebCrawler()
            self.crawler.warmup()
            logger.info(f"{LogEmoji.SUCCESS} Analyzer ready!")

    async def analyze_site(self, url: str, sample_pages: int = 3) -> SiteAnalysis:
        """
        Analyze a real estate website to understand structure

        Args:
            url: Homepage or listing page URL
            sample_pages: Number of pages to analyze

        Returns:
            SiteAnalysis with detected patterns and recommendations
        """
        logger.info(f"{LogEmoji.SEARCH} Analyzing site: {url}")

        if not self.crawler:
            self.warmup()

        # Step 1: Fetch sample pages
        logger.info(f"{LogEmoji.INFO} Fetching {sample_pages} sample pages...")
        html_samples = await self._fetch_samples(url, sample_pages)

        # Step 2: Analyze HTML structure with LLM
        logger.info(f"{LogEmoji.AI} Using GPT-4 to analyze structure...")
        structure = await self._analyze_with_llm(html_samples, url)

        # Step 3: Validate selectors
        logger.info(f"{LogEmoji.SUCCESS} Validating detected selectors...")
        validated = await self._validate_selectors(html_samples[0], structure)

        # Step 4: Detect rate limits and technical details
        logger.info(f"{LogEmoji.SEARCH} Detecting rate limits and protections...")
        technical = await self._detect_technical(url, html_samples)

        # Step 5: Assess data quality
        logger.info(f"{LogEmoji.CHART} Assessing data quality...")
        quality = await self._assess_quality(html_samples[0], validated)

        # Step 6: Build SiteAnalysis
        analysis = SiteAnalysis(
            site_domain=self._extract_domain(url),
            site_name=structure.get('site_name', self._extract_domain(url)),
            base_url=self._extract_base_url(url),

            # Selectors (required)
            property_card_selector=validated['card_selector'],
            title_selector=validated['title_selector'],
            price_selector=validated['price_selector'],
            location_selector=validated['location_selector'],
            link_selector=validated['link_selector'],

            # Pagination
            pagination_pattern=structure.get('pagination_pattern', '/p{page}'),
            max_pages_estimate=structure.get('max_pages', 100),
            properties_per_page=validated['items_per_page'],

            # Data fields
            data_fields=quality['available_fields'],

            # Technical
            rate_limit_seconds=technical['rate_limit'],
            max_workers=technical['max_workers'],
            has_cloudflare=technical['has_cloudflare'],
            requires_js=technical['requires_js'],

            # Quality
            quality_score=quality['score'],
            data_completeness=quality['completeness'],
            recommended_frequency=quality['frequency'],

            # Metadata
            analyzed_at=datetime.now(),
            analysis_confidence=validated['confidence'],
            notes=structure.get('notes', ''),

            # Optional selectors
            area_selector=validated.get('area_selector', ''),
            description_selector=validated.get('description_selector', ''),
            image_selector=validated.get('image_selector')
        )

        logger.info(f"{LogEmoji.SUCCESS} Analysis complete!")
        logger.info(f"{LogEmoji.CHART} Quality Score: {analysis.quality_score}/10")
        logger.info(f"{LogEmoji.INFO} Recommended Rate Limit: {analysis.rate_limit_seconds}s")
        logger.info(f"{LogEmoji.INFO} Max Workers: {analysis.max_workers}")

        return analysis

    async def _fetch_samples(self, url: str, count: int) -> List[str]:
        """Fetch sample pages for analysis"""
        samples = []

        # Fetch first page
        result = self.crawler.run(url=url)
        if result.success:
            samples.append(result.html)

        # Try to fetch additional pages
        for i in range(2, count + 1):
            # Try common pagination patterns
            for pattern in [f"/p{i}", f"?page={i}", f"/page/{i}"]:
                test_url = url.rstrip('/') + pattern
                result = self.crawler.run(url=test_url)
                if result.success and len(result.html) > 1000:
                    samples.append(result.html)
                    break

            await asyncio.sleep(1)  # Be polite

        return samples

    async def _analyze_with_llm(self, html_samples: List[str], url: str) -> Dict[str, Any]:
        """Use LLM (via Core Gateway) to analyze HTML structure"""

        # Take first sample and extract relevant portion
        soup = BeautifulSoup(html_samples[0], 'html.parser')

        # Find property listings (common patterns)
        sample_html = self._extract_listing_section(soup)

        prompt = f"""You are an expert web scraper analyzing a real estate website.

URL: {url}

HTML Sample (listing section):
{sample_html[:4000]}

Analyze this real estate website and provide JSON with:

1. site_name: Website name
2. card_selector: CSS selector for property card container
3. title_selector: CSS selector for property title (relative to card)
4. price_selector: CSS selector for price
5. location_selector: CSS selector for location
6. area_selector: CSS selector for area/size
7. description_selector: CSS selector for description
8. link_selector: CSS selector for property detail link
9. image_selector: CSS selector for property image
10. pagination_pattern: URL pattern for pagination (e.g., "/p{{page}}", "?page={{page}}")
11. max_pages: Estimated maximum pages (look for pagination)
12. notes: Any special notes about the site

Return ONLY valid JSON, no explanation.

Example:
{{
  "site_name": "Batdongsan.com.vn",
  "card_selector": ".re__card-full",
  "title_selector": ".re__card-title",
  "price_selector": ".re__card-config-price",
  "location_selector": ".re__card-location",
  "area_selector": ".re__card-config-area",
  "description_selector": ".re__card-description",
  "link_selector": "a",
  "image_selector": "img",
  "pagination_pattern": "/p{{page}}",
  "max_pages": 500,
  "notes": "High quality data, updates daily"
}}
"""

        # Call Core Gateway (uses Ollama by default, no rate limits!)
        import os
        core_gateway_url = os.getenv('CORE_GATEWAY_URL', 'http://localhost:8080')

        # Create proper LLMRequest using shared models
        llm_request = LLMRequest(
            model=ModelType.OLLAMA_QWEN25,  # Use Ollama (free, no rate limits)
            messages=[
                Message(role="system", content="You are an expert web scraper. Return only valid JSON."),
                Message(role="user", content=prompt)
            ],
            temperature=0.1,
            max_tokens=1000
        )

        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for Ollama
            response = await client.post(
                f"{core_gateway_url}/chat/completions",
                json=llm_request.dict()
            )
            response.raise_for_status()

            result = response.json()
            content = result['content']

            # Extract JSON from response
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            structure = json.loads(content.strip())

        logger.info(f"{LogEmoji.SUCCESS} LLM analysis complete: {structure.get('site_name')}")
        return structure

    def _extract_listing_section(self, soup: BeautifulSoup) -> str:
        """Extract the main listing section from full HTML"""

        # Common container patterns for real estate listings
        patterns = [
            {'class': lambda x: x and any(k in ' '.join(x).lower() for k in ['property', 'listing', 'card', 'item', 'product'])},
            {'id': lambda x: x and any(k in x.lower() for k in ['listing', 'property', 'result'])},
        ]

        for pattern in patterns:
            container = soup.find('div', pattern)
            if container:
                # Get parent container
                parent = container.find_parent(['div', 'section', 'main'])
                if parent:
                    return str(parent)[:4000]

        # Fallback: return body section
        body = soup.find('body')
        return str(body)[:4000] if body else str(soup)[:4000]

    async def _validate_selectors(self, html: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that selectors actually work"""

        soup = BeautifulSoup(html, 'html.parser')

        # Test card selector
        cards = soup.select(structure['card_selector'])

        if not cards:
            logger.warning(f"{LogEmoji.WARNING} Card selector '{structure['card_selector']}' found 0 items")
            confidence = 0.3
        else:
            confidence = min(1.0, len(cards) / 10)  # More cards = higher confidence

            # Test nested selectors on first card
            card = cards[0]
            for key in ['title_selector', 'price_selector', 'location_selector', 'link_selector']:
                selector = structure.get(key)
                if selector:
                    element = card.select_one(selector)
                    if not element:
                        logger.warning(f"{LogEmoji.WARNING} Selector '{selector}' not found in card")
                        confidence *= 0.8

        return {
            'card_selector': structure['card_selector'],
            'title_selector': structure.get('title_selector', ''),
            'price_selector': structure.get('price_selector', ''),
            'location_selector': structure.get('location_selector', ''),
            'area_selector': structure.get('area_selector', ''),
            'description_selector': structure.get('description_selector', ''),
            'link_selector': structure.get('link_selector', 'a'),
            'image_selector': structure.get('image_selector'),
            'items_per_page': len(cards),
            'confidence': confidence
        }

    async def _detect_technical(self, url: str, html_samples: List[str]) -> Dict[str, Any]:
        """Detect rate limits and technical protections"""

        has_cloudflare = any('cloudflare' in html.lower() or 'cf-ray' in html.lower() for html in html_samples)
        requires_js = any('javascript' in html.lower() and 'enable' in html.lower() for html in html_samples)

        # Estimate rate limit based on protections
        if has_cloudflare:
            rate_limit = 3.0
            max_workers = 3
        elif requires_js:
            rate_limit = 2.5
            max_workers = 4
        else:
            rate_limit = 2.0
            max_workers = 5

        return {
            'rate_limit': rate_limit,
            'max_workers': max_workers,
            'has_cloudflare': has_cloudflare,
            'requires_js': requires_js
        }

    async def _assess_quality(self, html: str, validated: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality of the site"""

        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select(validated['card_selector'])

        if not cards:
            return {
                'score': 1.0,
                'completeness': 0.0,
                'available_fields': [],
                'frequency': 'weekly'
            }

        # Check first 5 cards for data completeness
        available_fields = []
        field_counts = {'title': 0, 'price': 0, 'location': 0, 'area': 0, 'description': 0}

        for card in cards[:5]:
            if validated['title_selector'] and card.select_one(validated['title_selector']):
                field_counts['title'] += 1
                if 'title' not in available_fields:
                    available_fields.append('title')

            if validated['price_selector'] and card.select_one(validated['price_selector']):
                field_counts['price'] += 1
                if 'price' not in available_fields:
                    available_fields.append('price')

            if validated['location_selector'] and card.select_one(validated['location_selector']):
                field_counts['location'] += 1
                if 'location' not in available_fields:
                    available_fields.append('location')

            if validated['area_selector'] and card.select_one(validated['area_selector']):
                field_counts['area'] += 1
                if 'area' not in available_fields:
                    available_fields.append('area')

            if validated['description_selector'] and card.select_one(validated['description_selector']):
                field_counts['description'] += 1
                if 'description' not in available_fields:
                    available_fields.append('description')

        # Calculate completeness
        total_fields = len([k for k, v in field_counts.items() if v > 0])
        completeness = total_fields / 5.0

        # Calculate quality score
        score = 0.0
        score += 3.0 if field_counts['title'] >= 4 else 1.0
        score += 3.0 if field_counts['price'] >= 4 else 1.0
        score += 2.0 if field_counts['location'] >= 4 else 0.5
        score += 1.0 if field_counts['area'] >= 3 else 0.0
        score += 1.0 if field_counts['description'] >= 3 else 0.0

        # Recommend frequency based on quality
        if score >= 8.0:
            frequency = 'hourly'
        elif score >= 5.0:
            frequency = 'daily'
        else:
            frequency = 'weekly'

        return {
            'score': round(score, 1),
            'completeness': round(completeness, 2),
            'available_fields': available_fields,
            'frequency': frequency
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    def _extract_base_url(self, url: str) -> str:
        """Extract base URL (remove pagination, filters)"""
        from urllib.parse import urlparse
        parsed = urlparse(url)

        # Remove common pagination patterns
        path = parsed.path
        for pattern in ['/p1', '/p2', '/page/1', '/page/2']:
            path = path.replace(pattern, '')

        return f"{parsed.scheme}://{parsed.netloc}{path}"


# CLI for testing
async def main():
    """Test site analyzer"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python site_analyzer.py <url>")
        print("Example: python site_analyzer.py https://batdongsan.com.vn/nha-dat-ban")
        sys.exit(1)

    url = sys.argv[1]

    analyzer = SiteAnalyzer()
    analysis = await analyzer.analyze_site(url)

    print("\n" + "="*70)
    print("SITE ANALYSIS RESULTS")
    print("="*70)
    print(json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False))
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
