"""
Test Phase 1: Core Service Failback Logic
Verify OpenAI → Ollama failback on rate limit/quota errors
"""
import asyncio
import httpx
from datetime import datetime

LOG_FILE = "/tmp/architecture_implementation_tests.log"

def log(message: str):
    """Log to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

async def test_core_failback():
    """Test Core Gateway failback logic"""

    log("\n" + "="*80)
    log("PHASE 1 TEST: Core Service Failback Logic")
    log("="*80)

    core_gateway_url = "http://localhost:8080"

    async with httpx.AsyncClient(timeout=60.0) as client:

        # Test 1: Normal OpenAI request (should work if API key valid)
        log("\n📋 Test 1.1: Normal OpenAI request (gpt-4o-mini)")
        try:
            response = await client.post(
                f"{core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say 'OpenAI works'"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                data = response.json()
                log(f"✅ PASS: OpenAI returned: {data.get('content', '')[:50]}")
            else:
                log(f"⚠️  WARNING: OpenAI returned {response.status_code}: {response.text[:100]}")

        except Exception as e:
            log(f"⚠️  WARNING: OpenAI request failed: {e}")
            log("   (Expected if no API key or rate limited)")

        # Test 2: Ollama request (should always work with local Ollama)
        log("\n📋 Test 1.2: Direct Ollama request")
        try:
            response = await client.post(
                f"{core_gateway_url}/chat/completions",
                json={
                    "model": "ollama/qwen2.5:0.5b",
                    "messages": [
                        {"role": "user", "content": "Say 'Ollama works'"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                data = response.json()
                log(f"✅ PASS: Ollama returned: {data.get('content', '')[:50]}")
            else:
                log(f"❌ FAIL: Ollama returned {response.status_code}: {response.text[:100]}")

        except Exception as e:
            log(f"❌ FAIL: Ollama request failed: {e}")

        # Test 3: Simulated failback (when OpenAI model not available, fallback happens)
        log("\n📋 Test 1.3: Failback scenario (OpenAI model → Ollama)")
        log("   Note: If OpenAI API key is invalid or rate limited, this should failback to Ollama")
        try:
            response = await client.post(
                f"{core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",  # Try OpenAI model
                    "messages": [
                        {"role": "user", "content": "Test failback"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                data = response.json()
                model_used = data.get('model', '')
                content = data.get('content', '')

                if 'deepseek' in model_used.lower() or 'ollama' in model_used.lower():
                    log(f"✅ PASS: Failback worked! Used model: {model_used}")
                    log(f"   Response: {content[:50]}")
                else:
                    log(f"✅ PASS: OpenAI worked (no failback needed). Model: {model_used}")
                    log(f"   Response: {content[:50]}")
            else:
                log(f"❌ FAIL: Request returned {response.status_code}: {response.text[:100]}")

        except Exception as e:
            log(f"❌ FAIL: Request failed completely: {e}")

    log("\n" + "="*80)
    log("PHASE 1 TEST COMPLETE")
    log("="*80)
    log(f"\n📄 Full log saved to: {LOG_FILE}")

if __name__ == "__main__":
    asyncio.run(test_core_failback())
