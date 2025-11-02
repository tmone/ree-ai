"""
Quick Script: Normalize all price fields in OpenSearch
Adds price_normalized field (numeric) for proper range filtering
"""
import asyncio
import sys
import re
from pathlib import Path
from opensearchpy import AsyncOpenSearch
from tqdm.asyncio import tqdm

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger("price_fix")


def normalize_price(price_str: str) -> float:
    """
    Normalize Vietnamese price strings to numeric values

    Examples:
        "3,19 tỷ" → 3190000000
        "2 tỷ" → 2000000000
        "500 triệu" → 500000000
        "Thỏa thuận" → 0
    """
    if not price_str or not isinstance(price_str, str):
        return 0

    price_str = price_str.strip().lower()

    # Handle negotiable prices
    if any(keyword in price_str for keyword in ["thỏa thuận", "liên hệ", "contact"]):
        return 0

    try:
        # Remove commas and extra spaces
        price_str = price_str.replace(",", ".").replace(" ", "")

        # Extract number
        number_match = re.search(r'(\d+(?:\.\d+)?)', price_str)
        if not number_match:
            return 0

        number = float(number_match.group(1))

        # Check unit
        if "tỷ" in price_str or "billion" in price_str:
            return number * 1_000_000_000
        elif "triệu" in price_str or "million" in price_str:
            return number * 1_000_000
        elif "nghìn" in price_str or "thousand" in price_str:
            return number * 1_000
        else:
            # Assume it's already in VND if no unit
            return number

    except Exception as e:
        logger.warning(f"Failed to parse price '{price_str}': {e}")
        return 0


async def fix_all_prices(batch_size: int = 100):
    """Fix all price fields in OpenSearch"""

    logger.info("🚀 Starting price normalization fix...")

    # Connect to OpenSearch
    opensearch_client = AsyncOpenSearch(
        hosts=[{
            'host': settings.OPENSEARCH_HOST,
            'port': settings.OPENSEARCH_PORT
        }],
        http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD) if settings.OPENSEARCH_USER else None,
        use_ssl=settings.OPENSEARCH_USE_SSL,
        verify_certs=settings.OPENSEARCH_VERIFY_CERTS
    )

    index_name = settings.OPENSEARCH_PROPERTIES_INDEX
    logger.info(f"📊 Connected to OpenSearch index: {index_name}")

    # Count total documents
    count_response = await opensearch_client.count(index=index_name)
    total_docs = count_response['count']
    logger.info(f"📈 Total documents to process: {total_docs}")

    # Process in batches using scroll API
    processed = 0
    updated = 0

    # Initial search with scroll
    response = await opensearch_client.search(
        index=index_name,
        scroll='5m',
        size=batch_size,
        body={
            "query": {"match_all": {}},
            "_source": ["price"]
        }
    )

    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']

    # Progress bar
    pbar = tqdm(total=total_docs, desc="Normalizing prices")

    while hits:
        # Prepare bulk update
        bulk_body = []

        for hit in hits:
            doc_id = hit['_id']
            price_str = hit['_source'].get('price', '')
            price_normalized = normalize_price(price_str)

            # Update action
            bulk_body.append({"update": {"_index": index_name, "_id": doc_id}})
            bulk_body.append({
                "doc": {
                    "price_normalized": price_normalized
                }
            })

            if price_normalized > 0:
                updated += 1

        # Execute bulk update
        if bulk_body:
            await opensearch_client.bulk(body=bulk_body, refresh=False)

        processed += len(hits)
        pbar.update(len(hits))

        # Get next batch
        response = await opensearch_client.scroll(
            scroll_id=scroll_id,
            scroll='5m'
        )
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']

    pbar.close()

    # Clear scroll
    await opensearch_client.clear_scroll(scroll_id=scroll_id)

    # Refresh index to make updates visible
    logger.info("🔄 Refreshing index...")
    await opensearch_client.indices.refresh(index=index_name)

    await opensearch_client.close()

    logger.info(f"✅ Migration completed!")
    logger.info(f"📊 Processed: {processed} documents")
    logger.info(f"💰 Updated with normalized prices: {updated}")
    logger.info(f"💸 Skipped (negotiable/invalid): {processed - updated}")


if __name__ == "__main__":
    asyncio.run(fix_all_prices())
