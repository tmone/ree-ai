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
            language: Target language code (vi, en, th, ja)
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


# Export
__all__ = ['I18n', 'i18n', 't']
