"""
LLM-based Translation Service
Translates real estate terms to English using LLM (context-aware)
"""
import json
import re
from typing import Dict, Optional
import httpx
from shared.utils.logger import setup_logger, LogEmoji


class LLMTranslator:
    """
    Translate real estate terms using LLM via Core Gateway
    Context-aware translation for better accuracy
    """

    def __init__(self, core_gateway_url: str):
        self.core_gateway_url = core_gateway_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.logger = setup_logger("llm_translator")

    async def translate_to_english(
        self,
        value: str,
        source_language: str,
        context: Optional[str] = None,
        property_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Translate a term to English using LLM

        Args:
            value: Term to translate (e.g., "hầm rượu")
            source_language: Source language code ('vi', 'zh', etc.)
            context: Optional context sentence
            property_name: Type of property attribute (e.g., "amenity", "furniture")

        Returns:
            Translation result:
            {
                "english": "wine_cellar",
                "normalized": "wine_cellar",
                "confidence": 0.95,
                "suggested_translations": {
                    "vi": "Hầm rượu",
                    "en": "Wine cellar",
                    "zh": "酒窖"
                }
            }
        """
        try:
            # Build context-aware prompt
            prompt = self._build_translation_prompt(
                value, source_language, context, property_name
            )

            # Call LLM
            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a real estate translation expert. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.2  # Low temperature for consistent translation
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request
            )

            if response.status_code != 200:
                self.logger.error(
                    f"{LogEmoji.ERROR} LLM translation failed: {response.status_code}"
                )
                return self._fallback_translation(value)

            data = response.json()
            content = data.get("content", "").strip()

            # Parse JSON response
            content = re.sub(r'^```(?:json)?\s*\n?', '', content)
            content = re.sub(r'\n?```\s*$', '', content)
            content = content.strip()

            translation_result = json.loads(content)

            self.logger.info(
                f"{LogEmoji.SUCCESS} Translated '{value}' → '{translation_result.get('english')}'"
            )

            return translation_result

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} LLM translation error: {e}")
            return self._fallback_translation(value)

    def _build_translation_prompt(
        self,
        value: str,
        source_language: str,
        context: Optional[str],
        property_name: Optional[str]
    ) -> str:
        """Build prompt for LLM translation"""

        lang_name = {
            'vi': 'Vietnamese',
            'zh': 'Chinese',
            'ko': 'Korean',
            'ja': 'Japanese'
        }.get(source_language, source_language)

        context_info = ""
        if context:
            context_info = f"\n**Context sentence**: {context}"

        property_info = ""
        if property_name:
            property_info = f"\n**Property attribute type**: {property_name}"

        prompt = f"""You are translating a real estate term from {lang_name} to English.

**Term to translate**: "{value}"
{context_info}
{property_info}

**Requirements**:
1. Translate to **standard English real estate terminology**
2. Use **snake_case** format (e.g., "wine_cellar", "swimming_pool")
3. Be **specific and accurate** - this is for database storage
4. Provide translations for multiple languages (vi, en, zh)

**Output Format** (JSON only):
```json
{{
  "english": "wine_cellar",
  "normalized": "wine_cellar",
  "confidence": 0.95,
  "suggested_translations": {{
    "vi": "Hầm rượu",
    "en": "Wine cellar",
    "zh": "酒窖"
  }},
  "category": "private_amenity",
  "description": "Private wine storage room"
}}
```

**Examples**:

Input: "hầm rượu" (Vietnamese, amenity)
Output:
```json
{{
  "english": "wine_cellar",
  "normalized": "wine_cellar",
  "confidence": 0.98,
  "suggested_translations": {{
    "vi": "Hầm rượu",
    "en": "Wine cellar",
    "zh": "酒窖"
  }},
  "category": "private_amenity",
  "description": "Private wine storage cellar"
}}
```

Input: "view biển" (Vietnamese, view_type)
Output:
```json
{{
  "english": "sea_view",
  "normalized": "sea_view",
  "confidence": 1.0,
  "suggested_translations": {{
    "vi": "View biển",
    "en": "Sea view",
    "zh": "海景"
  }},
  "category": "natural",
  "description": "Overlooking sea or ocean"
}}
```

Now translate: "{value}"

Return ONLY valid JSON, no explanation:"""

        return prompt

    def _fallback_translation(self, value: str) -> Dict[str, str]:
        """
        Fallback translation when LLM fails
        Simple normalization
        """
        # Basic normalization: lowercase + replace spaces with underscores
        normalized = value.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove special chars
        normalized = re.sub(r'\s+', '_', normalized)  # Replace spaces with _

        return {
            "english": normalized,
            "normalized": normalized,
            "confidence": 0.5,  # Low confidence for fallback
            "suggested_translations": {
                "en": value  # Keep original as fallback
            },
            "category": "unknown",
            "description": f"Auto-normalized from: {value}"
        }

    async def batch_translate(
        self,
        items: list[Dict[str, str]],
        source_language: str
    ) -> list[Dict[str, str]]:
        """
        Translate multiple items in batch

        Args:
            items: List of items to translate
                [{"value": "hầm rượu", "property_name": "amenity"}, ...]
            source_language: Source language code

        Returns:
            List of translation results
        """
        results = []

        for item in items:
            result = await self.translate_to_english(
                value=item.get("value", ""),
                source_language=source_language,
                context=item.get("context"),
                property_name=item.get("property_name")
            )
            results.append(result)

        return results

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
