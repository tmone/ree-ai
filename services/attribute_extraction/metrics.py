"""
Prometheus Metrics for Master Data Extraction System

This module defines and tracks metrics for:
- Master data growth
- Extraction performance
- Fuzzy matching accuracy
- Pending items queue
- Translation coverage
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional

# =============================================================================
# Master Data Metrics
# =============================================================================

master_data_total_records = Gauge(
    'master_data_total_records',
    'Total number of records in each master data table',
    ['table']
)

master_data_translations_count = Gauge(
    'master_data_translations_count',
    'Number of translations for each table and language',
    ['table', 'lang']
)

# =============================================================================
# Pending Master Data Metrics
# =============================================================================

pending_master_data_count = Gauge(
    'pending_master_data_count',
    'Number of pending master data items by status',
    ['status']
)

pending_master_data_frequency = Gauge(
    'pending_master_data_frequency',
    'Frequency count of pending items',
    ['value_english', 'suggested_table']
)

# =============================================================================
# Extraction Metrics
# =============================================================================

extraction_requests_total = Counter(
    'extraction_requests_total',
    'Total number of extraction requests',
    ['language', 'status']
)

extraction_request_duration_seconds = Histogram(
    'extraction_request_duration_seconds',
    'Time spent processing extraction requests',
    ['language'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

extraction_errors_total = Counter(
    'extraction_errors_total',
    'Total number of extraction errors',
    ['error_type']
)

# =============================================================================
# Fuzzy Matching Metrics
# =============================================================================

fuzzy_match_total = Counter(
    'fuzzy_match_total',
    'Total number of fuzzy matches attempted',
    ['attribute_type', 'match_method']
)

fuzzy_match_confidence = Histogram(
    'fuzzy_match_confidence',
    'Confidence scores of fuzzy matches',
    ['attribute_type'],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

fuzzy_match_duration_seconds = Histogram(
    'fuzzy_match_duration_seconds',
    'Time spent on fuzzy matching',
    ['attribute_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

# =============================================================================
# LLM Translation Metrics
# =============================================================================

llm_translation_requests_total = Counter(
    'llm_translation_requests_total',
    'Total number of LLM translation requests',
    ['source_lang', 'status']
)

llm_translation_duration_seconds = Histogram(
    'llm_translation_duration_seconds',
    'Time spent on LLM translations',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0]
)

# =============================================================================
# Crawler Metrics
# =============================================================================

crawler_listings_scraped_total = Counter(
    'crawler_listings_scraped_total',
    'Total number of listings scraped',
    ['site']
)

crawler_new_attributes_discovered_total = Counter(
    'crawler_new_attributes_discovered_total',
    'Total number of new attributes discovered by crawler',
    ['site', 'attribute_type']
)

crawler_errors_total = Counter(
    'crawler_errors_total',
    'Total number of crawler errors',
    ['site', 'error_type']
)

crawler_duration_seconds = Histogram(
    'crawler_duration_seconds',
    'Time spent crawling per site',
    ['site'],
    buckets=[10, 30, 60, 120, 300, 600]
)

# =============================================================================
# Database Metrics
# =============================================================================

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Time spent on database queries',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

database_errors_total = Counter(
    'database_errors_total',
    'Total number of database errors',
    ['error_type']
)

database_connection_pool_size = Gauge(
    'database_connection_pool_size',
    'Current size of database connection pool'
)

database_connection_pool_available = Gauge(
    'database_connection_pool_available',
    'Number of available connections in pool'
)

# =============================================================================
# System Info
# =============================================================================

system_info = Info(
    'master_data_system',
    'Information about the master data extraction system'
)

# Set system info
system_info.info({
    'version': '1.0.0',
    'service': 'attribute_extraction',
    'supported_languages': 'vi,en,zh,ko,ja'
})


# =============================================================================
# Helper Functions
# =============================================================================

def track_extraction_request(language: str, duration: float, success: bool):
    """Track an extraction request"""
    status = 'success' if success else 'error'
    extraction_requests_total.labels(language=language, status=status).inc()
    extraction_request_duration_seconds.labels(language=language).observe(duration)


def track_fuzzy_match(attribute_type: str, method: str, confidence: float, duration: float):
    """Track a fuzzy match operation"""
    fuzzy_match_total.labels(attribute_type=attribute_type, match_method=method).inc()
    fuzzy_match_confidence.labels(attribute_type=attribute_type).observe(confidence)
    fuzzy_match_duration_seconds.labels(attribute_type=attribute_type).observe(duration)


def track_llm_translation(source_lang: str, duration: float, success: bool):
    """Track an LLM translation request"""
    status = 'success' if success else 'error'
    llm_translation_requests_total.labels(source_lang=source_lang, status=status).inc()
    llm_translation_duration_seconds.observe(duration)


def track_crawler_run(site: str, listings_count: int, new_attrs_count: int, duration: float):
    """Track a crawler run"""
    crawler_listings_scraped_total.labels(site=site).inc(listings_count)
    crawler_duration_seconds.labels(site=site).observe(duration)


def track_new_attribute_discovered(site: str, attribute_type: str, count: int = 1):
    """Track discovery of new attributes"""
    crawler_new_attributes_discovered_total.labels(
        site=site,
        attribute_type=attribute_type
    ).inc(count)


def track_error(error_type: str, service: str = 'extraction'):
    """Track an error"""
    if service == 'extraction':
        extraction_errors_total.labels(error_type=error_type).inc()
    elif service == 'crawler':
        crawler_errors_total.labels(site='unknown', error_type=error_type).inc()
    elif service == 'database':
        database_errors_total.labels(error_type=error_type).inc()


# =============================================================================
# Background Metrics Collection
# =============================================================================

async def update_master_data_metrics(db_pool):
    """
    Update master data metrics from database
    Should be called periodically (e.g., every 60 seconds)
    """
    async with db_pool.acquire() as conn:
        # Update total records per table
        tables = [
            'cities', 'districts', 'wards', 'streets',
            'property_types', 'amenities', 'directions',
            'furniture_types', 'legal_statuses', 'view_types'
        ]

        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            master_data_total_records.labels(table=table).set(count)

        # Update translation counts
        for table in tables:
            translation_table = f"{table}_translations"
            try:
                # Count by language
                rows = await conn.fetch(f"""
                    SELECT lang_code, COUNT(*) as count
                    FROM {translation_table}
                    GROUP BY lang_code
                """)

                for row in rows:
                    master_data_translations_count.labels(
                        table=table,
                        lang=row['lang_code']
                    ).set(row['count'])
            except Exception:
                # Table might not have translations
                pass

        # Update pending items count
        pending_counts = await conn.fetch("""
            SELECT status, COUNT(*) as count
            FROM pending_master_data
            GROUP BY status
        """)

        for row in pending_counts:
            pending_master_data_count.labels(status=row['status']).set(row['count'])

        # Update pending items frequency (top 20)
        top_pending = await conn.fetch("""
            SELECT value_english, suggested_table, frequency
            FROM pending_master_data
            WHERE status = 'pending'
            ORDER BY frequency DESC
            LIMIT 20
        """)

        # Reset all pending frequency metrics first
        pending_master_data_frequency._metrics.clear()

        for row in top_pending:
            pending_master_data_frequency.labels(
                value_english=row['value_english'],
                suggested_table=row['suggested_table']
            ).set(row['frequency'])


async def update_database_pool_metrics(db_pool):
    """Update database connection pool metrics"""
    database_connection_pool_size.set(db_pool.get_size())
    database_connection_pool_available.set(db_pool.get_idle_size())
