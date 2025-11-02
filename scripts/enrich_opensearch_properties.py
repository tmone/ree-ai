"""
Migration Script: Enrich OpenSearch Properties with LLM-extracted Metadata

Fixes 20K+ existing documents by extracting:
- city (from location)
- district (from location)
- property_type (from title)

Uses LLM (no hardcoding!) with caching for efficiency.
"""
import asyncio
import sys
from pathlib import Path
import json
import re
import httpx
from typing import Dict, List
from opensearchpy import AsyncOpenSearch
from tqdm.asyncio import tqdm

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger("migration")

# Cache for LLM extractions (avoid redundant calls)
extraction_cache: Dict[str, Dict[str, str]] = {}


async def extract_metadata_with_llm(
    http_client: httpx.AsyncClient,
    core_gateway_url: str,
    title: str,
    location: str
) -> Dict[str, str]:
    """Extract city, district, property_type using LLM"""

    cache_key = f"{title[:50]}_{location[:30]}"

    # Check cache
    if cache_key in extraction_cache:
        return extraction_cache[cache_key]

    try:
        prompt = f"""Extract structured metadata from this Vietnamese real estate listing.

Title: {title}
Location: {location}

Return ONLY valid JSON:
{{
    "city": "Hồ Chí Minh" | "Hà Nội" | etc,
    "district": "Quận 1" | "Thủ Đức" | etc,
    "property_type": "căn hộ" | "nhà phố" | "biệt thự" | "đất" | etc
}}

Rules:
- Infer city from district ("Quận 2" → "Hồ Chí Minh")
- Normalize district ("Q2" → "Quận 2")
- Extract type from title
- Empty string if not found

JSON:"""

        response = await http_client.post(
            f"{core_gateway_url}/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.0
            },
            timeout=15.0
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "").strip()

            # Clean markdown
            content = re.sub(r'^```(?:json)?\s*\n?', '', content)
            content = re.sub(r'\n?```\s*$', '', content)

            metadata = json.loads(content)

            # Cache result
            extraction_cache[cache_key] = metadata

            return metadata
        else:
            return {"city": "", "district": "", "property_type": ""}

    except Exception as e:
        logger.warning(f"LLM extraction error: {e}")
        return {"city": "", "district": "", "property_type": ""}


async def enrich_batch(
    opensearch_client: AsyncOpenSearch,
    http_client: httpx.AsyncClient,
    core_gateway_url: str,
    documents: List[Dict],
    index_name: str
):
    """Enrich a batch of documents with metadata"""

    # Extract metadata for all docs in parallel
    extraction_tasks = [
        extract_metadata_with_llm(
            http_client,
            core_gateway_url,
            doc["_source"]["title"],
            doc["_source"].get("location", "")
        )
        for doc in documents
    ]

    metadatas = await asyncio.gather(*extraction_tasks)

    # Prepare bulk update
    bulk_body = []
    for doc, metadata in zip(documents, metadatas):
        doc_id = doc["_id"]

        # Update action
        bulk_body.append({"update": {"_index": index_name, "_id": doc_id}})
        bulk_body.append({
            "doc": {
                "city": metadata.get("city", ""),
                "district": metadata.get("district", ""),
                "property_type": metadata.get("property_type", "")
            }
        })

    # Execute bulk update
    if bulk_body:
        await opensearch_client.bulk(body=bulk_body)

    return len(documents)


async def migrate_all_properties(
    batch_size: int = 50,
    max_docs: int = None
):
    """
    Migrate all properties in OpenSearch

    Args:
        batch_size: Number of docs to process per batch
        max_docs: Maximum docs to process (for testing)
    """

    logger.info("🚀 Starting OpenSearch property enrichment migration...")

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

    # HTTP client for LLM calls
    http_client = httpx.AsyncClient(timeout=30.0)
    core_gateway_url = settings.get_core_gateway_url()

    index_name = settings.OPENSEARCH_PROPERTIES_INDEX

    logger.info(f"📊 Connected to OpenSearch index: {index_name}")

    # Count total documents
    count_response = await opensearch_client.count(index=index_name)
    total_docs = count_response["count"]

    if max_docs:
        total_docs = min(total_docs, max_docs)

    logger.info(f"📈 Total documents to process: {total_docs}")

    # Scroll through all documents
    processed = 0

    # Initial search
    response = await opensearch_client.search(
        index=index_name,
        body={
            "query": {"match_all": {}},
            "size": batch_size,
            "sort": ["_doc"]  # Fastest sort for scrolling
        },
        scroll="5m"
    )

    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    with tqdm(total=total_docs, desc="Enriching properties") as pbar:
        while hits and (max_docs is None or processed < max_docs):
            # Process batch
            batch = hits[:batch_size]
            await enrich_batch(opensearch_client, http_client, core_gateway_url, batch, index_name)

            processed += len(batch)
            pbar.update(len(batch))

            if max_docs and processed >= max_docs:
                break

            # Get next batch
            response = await opensearch_client.scroll(
                scroll_id=scroll_id,
                scroll="5m"
            )
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]

    # Cleanup scroll
    await opensearch_client.clear_scroll(scroll_id=scroll_id)

    # Cleanup clients
    await opensearch_client.close()
    await http_client.aclose()

    logger.info(f"\n✅ Migration completed!")
    logger.info(f"📊 Processed: {processed} documents")
    logger.info(f"💾 Cache size: {len(extraction_cache)} unique patterns")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrich OpenSearch properties with LLM-extracted metadata")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--max-docs", type=int, default=None, help="Max documents to process (for testing)")
    parser.add_argument("--test", action="store_true", help="Test mode: process only 100 docs")

    args = parser.parse_args()

    if args.test:
        print("🧪 TEST MODE: Processing only 100 documents")
        args.max_docs = 100

    asyncio.run(migrate_all_properties(
        batch_size=args.batch_size,
        max_docs=args.max_docs
    ))
