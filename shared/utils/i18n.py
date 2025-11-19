"""
Internationalization (i18n) utility for REE AI
Template-based translation system with hot reload support

Usage:
    from shared.utils.i18n import t

    # Simple translation
    message = t('errors.system_error', language='vi')

    # With template variables
    message = t('property_posting.acknowledgment',
                language='vi',
                transaction_type='bán')
"""
import json
import os
from typing import Dict, Optional, Any
from pathlib import Path


class I18n:
    """
    i18n manager with template support and hot reload.

    Features:
    - Load translations from JSON files
    - Template placeholders: {key}
    - Fallback to English if translation missing
    - Hot reload capability
    - Nested key support: 'errors.system_error'
    """

    _instance = None
    _translations: Dict[str, Dict] = {}

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize and load translations"""
        if not self._translations:
            self.load_all_translations()

    def load_all_translations(self, dirpath: Optional[str] = None):
        """
        Load all translation files from directory.

        Args:
            dirpath: Optional custom directory path
        """
        if dirpath is None:
            # Default: shared/data/translations/
            current_dir = Path(__file__).parent
            dirpath = current_dir.parent / 'data' / 'translations'

        dirpath = Path(dirpath)

        if not dirpath.exists():
            print(f"[WARNING] Translations directory not found: {dirpath}")
            return

        # Load all messages.*.json files
        for filepath in dirpath.glob('messages.*.json'):
            lang_code = filepath.stem.split('.')[-1]  # Extract 'vi' from 'messages.vi.json'
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
                # Avoid emoji printing on Windows - use ASCII
                print(f"[OK] Loaded i18n: {lang_code} ({filepath.name})")
            except Exception as e:
                print(f"[ERROR] Failed to load {filepath}: {e}")

    def reload(self):
        """Reload all translations (for hot reload)"""
        self._translations = {}
        self.load_all_translations()

    def get(
        self,
        key: str,
        language: str = 'vi',
        fallback_language: str = 'en',
        **kwargs
    ) -> str:
        """
        Get translated message with template substitution.

        Args:
            key: Translation key (supports nested: 'errors.system_error')
            language: Target language code (vi, en, th, ja, ko)
            fallback_language: Fallback if translation not found
            **kwargs: Template variables for substitution

        Returns:
            Translated message with substituted variables

        Examples:
            >>> i18n = I18n()
            >>> i18n.get('errors.system_error', language='vi')
            "Xin lỗi, hệ thống đang gặp sự cố..."

            >>> i18n.get('property_posting.acknowledgment', language='vi', transaction_type='bán')
            "Tuyệt vời, bạn muốn đăng tin bán!"
        """
        # Get translation dict for language
        translation_dict = self._translations.get(language, {})

        # Parse nested key (e.g., 'errors.system_error')
        keys = key.split('.')
        value = translation_dict

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        # Fallback to English if not found
        if value is None and language != fallback_language:
            translation_dict = self._translations.get(fallback_language, {})
            value = translation_dict
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = None
                    break

        # Final fallback to key itself
        if value is None:
            value = key

        # Template substitution
        if isinstance(value, str) and kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                print(f"[WARNING] Missing template variable in '{key}': {e}")

        return value

    def list_keys(self, language: str = 'vi', prefix: str = '') -> list:
        """
        List all available translation keys (for debugging).

        Args:
            language: Language code
            prefix: Optional prefix filter

        Returns:
            List of keys
        """
        translation_dict = self._translations.get(language, {})

        def _flatten_keys(d: dict, parent_key: str = '') -> list:
            """Recursively flatten nested dict keys"""
            items = []
            for k, v in d.items():
                if k in ['version', 'language', 'last_updated']:
                    continue
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten_keys(v, new_key))
                else:
                    items.append(new_key)
            return items

        all_keys = _flatten_keys(translation_dict)

        if prefix:
            return [k for k in all_keys if k.startswith(prefix)]
        return all_keys


# Singleton instance
i18n = I18n()


# Convenience function
def t(key: str, language: str = 'vi', **kwargs) -> str:
    """
    Shorthand for translation.

    Usage:
        from shared.utils.i18n import t

        message = t('errors.system_error', language='vi')
        message = t('property_posting.acknowledgment', language='vi', transaction_type='bán')
    """
    return i18n.get(key, language, **kwargs)


def detect_language_from_header(accept_language: Optional[str]) -> str:
    """
    Detect preferred language from HTTP Accept-Language header.

    Args:
        accept_language: Accept-Language header value (e.g., "vi-VN,vi;q=0.9,en-US;q=0.8")

    Returns:
        Detected language code (vi, en, th, ja, ko) or 'vi' as default

    Examples:
        >>> detect_language_from_header("vi-VN,vi;q=0.9,en-US;q=0.8")
        'vi'
        >>> detect_language_from_header("en-US,en;q=0.9")
        'en'
        >>> detect_language_from_header("th-TH,th;q=0.9")
        'th'
    """
    if not accept_language:
        return 'vi'

    # Supported languages
    supported = {'vi', 'en', 'th', 'ja', 'ko'}

    # Parse Accept-Language header
    # Format: "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    languages = []
    for item in accept_language.split(','):
        parts = item.strip().split(';')
        lang_code = parts[0].split('-')[0].lower()  # Extract 'vi' from 'vi-VN'

        # Get quality value (default 1.0)
        quality = 1.0
        if len(parts) > 1 and parts[1].startswith('q='):
            try:
                quality = float(parts[1][2:])
            except ValueError:
                quality = 1.0

        if lang_code in supported:
            languages.append((lang_code, quality))

    # Sort by quality (descending)
    if languages:
        languages.sort(key=lambda x: x[1], reverse=True)
        return languages[0][0]

    return 'vi'


async def detect_language_from_user_profile(
    user_id: Optional[str],
    db_gateway_url: str = "http://localhost:8081"
) -> Optional[str]:
    """
    Detect user's preferred language from their profile in database.

    Args:
        user_id: User ID
        db_gateway_url: DB Gateway service URL

    Returns:
        User's preferred language code or None if not found

    Examples:
        >>> await detect_language_from_user_profile("user123")
        'en'
    """
    if not user_id:
        return None

    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{db_gateway_url}/users/{user_id}",
                params={"fields": "preferred_language"}
            )

            if response.status_code == 200:
                data = response.json()
                lang = data.get("preferred_language")
                if lang in {'vi', 'en', 'th', 'ja', 'ko'}:
                    return lang

    except Exception as e:
        print(f"[WARNING] Failed to fetch user language preference: {e}")

    return None


def detect_language_from_country_code(country_code: Optional[str]) -> str:
    """
    Map country code to supported language.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'VN', 'TH', 'JP')

    Returns:
        Mapped language code or 'vi' as default

    Examples:
        >>> detect_language_from_country_code('VN')
        'vi'
        >>> detect_language_from_country_code('TH')
        'th'
        >>> detect_language_from_country_code('JP')
        'ja'
        >>> detect_language_from_country_code('US')
        'en'
    """
    if not country_code:
        return 'vi'

    country_to_lang = {
        'VN': 'vi',  # Vietnam
        'TH': 'th',  # Thailand
        'JP': 'ja',  # Japan
        'KR': 'ko',  # South Korea
        'US': 'en',  # United States
        'GB': 'en',  # United Kingdom
        'AU': 'en',  # Australia
        'CA': 'en',  # Canada
        'SG': 'en',  # Singapore
    }

    return country_to_lang.get(country_code.upper(), 'vi')


async def auto_detect_language(
    user_id: Optional[str] = None,
    accept_language: Optional[str] = None,
    country_code: Optional[str] = None,
    db_gateway_url: str = "http://localhost:8081",
    default: str = 'vi'
) -> str:
    """
    Auto-detect user's preferred language from multiple sources.

    Detection priority:
    1. User profile (from database) - highest priority
    2. HTTP Accept-Language header
    3. Country code (from IP geolocation)
    4. Default language - fallback

    Args:
        user_id: Optional user ID for profile lookup
        accept_language: Optional Accept-Language header
        country_code: Optional country code from IP geolocation
        db_gateway_url: DB Gateway service URL
        default: Default language if no detection succeeds

    Returns:
        Detected language code (vi, en, th, ja, ko)

    Examples:
        >>> await auto_detect_language(user_id="user123")
        'en'  # From user profile

        >>> await auto_detect_language(accept_language="th-TH,th;q=0.9")
        'th'  # From Accept-Language header

        >>> await auto_detect_language(country_code="JP")
        'ja'  # From country code

        >>> await auto_detect_language()
        'vi'  # Default fallback
    """
    # Priority 1: User profile
    if user_id:
        lang = await detect_language_from_user_profile(user_id, db_gateway_url)
        if lang:
            return lang

    # Priority 2: Accept-Language header
    if accept_language:
        lang = detect_language_from_header(accept_language)
        if lang != default:  # If detected something other than default
            return lang

    # Priority 3: Country code
    if country_code:
        lang = detect_language_from_country_code(country_code)
        if lang != default:
            return lang

    # Fallback
    return default


# Export
__all__ = [
    'I18n', 'i18n', 't',
    'detect_language_from_header',
    'detect_language_from_user_profile',
    'detect_language_from_country_code',
    'auto_detect_language'
]
