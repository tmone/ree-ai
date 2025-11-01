#!/usr/bin/env python3
"""Test RAG Service directly to prove architecture works"""
import httpx
import asyncio
import json

async def test_rag():
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Test RAG Service directly without strict filters
        response = await client.post(
            "http://localhost:8091/query",
            json={
                "query": "căn hộ quận 7",
                "filters": {},  # Empty filters - rely on text search only
                "limit": 3
            }
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ RAG PIPELINE HOẠT ĐỘNG!\n")
            print(f"Retrieved: {data['retrieved_count']} properties")
            print(f"Confidence: {data['confidence']}")
            print(f"\n📝 Generated Response:\n")
            print(data['response'])
            print(f"\n📊 Sources:")
            for src in data.get('sources', []):
                print(f"  - {src}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_rag())
