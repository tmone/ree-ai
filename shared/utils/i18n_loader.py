"""
i18n Master Data Loader Utility

CRITICAL: This is the SINGLE SOURCE OF TRUTH for loading multilingual data.
ALL services MUST use this loader - NEVER hardcode text!

Usage:
    from shared.utils.i18n_loader import I18nLoader

    i18n = I18nLoader()
    field_labels = i18n.get_field_labels('vi')
    listing_types = i18n.get_listing_type_keywords('vi')
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class I18nLoader:
    """
    Master data loader for i18n compliance

    ZERO TOLERANCE POLICY:
    - NO hardcoded fallbacks
    - System MUST fail if master data unavailable
    - ALL user-facing text comes from JSON
    """

    def __init__(self, master_data_path: Optional[Path] = None):
        """
        Initialize i18n loader

        Args:
            master_data_path: Path to multilingual_keywords.json
                            If None, auto-detect from shared/data/
        """
        if master_data_path is None:
            # Auto-detect path
            current_file = Path(__file__)
            master_data_path = current_file.parent.parent / "data" / "multilingual_keywords.json"

        self.master_data_path = master_data_path
        self._data: Optional[Dict] = None
        self._load_master_data()

    def _load_master_data(self):
        """
        Load master data from JSON

        CRITICAL: Must raise error if loading fails - NO silent fallbacks!
        """
        try:
            with open(self.master_data_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            logger.info(f"✅ Master data loaded successfully from {self.master_data_path}")
        except FileNotFoundError as e:
            error_msg = (
                f"CRITICAL: Master data file not found at {self.master_data_path}. "
                f"System cannot operate without i18n master data!"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = (
                f"CRITICAL: Master data JSON is invalid at {self.master_data_path}. "
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"CRITICAL: Failed to load master data from {self.master_data_path}. "
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_field_labels(self, lang: str = 'vi') -> Dict[str, str]:
        """
        Get field labels for specified language

        Args:
            lang: Language code (vi/en/th/ja)

        Returns:
            Dict of field_name -> label

        Example:
            labels = i18n.get_field_labels('vi')
            print(labels['title'])  # "Tiêu đề"
        """
        try:
            return self._data['field_labels'][lang]
        except KeyError:
            raise RuntimeError(
                f"Field labels not found for language '{lang}' in master data. "
                f"Available languages: {list(self._data.get('field_labels', {}).keys())}"
            )

    def get_listing_type_display(self, lang: str = 'vi') -> Dict[str, str]:
        """
        Get listing type display names (sale -> 'Bán', rent -> 'Cho thuê')

        Args:
            lang: Language code (vi/en/th/ja)

        Returns:
            Dict mapping 'sale'/'rent' to display names

        Example:
            types = i18n.get_listing_type_display('vi')
            print(types['sale'])  # "bán"
            print(types['rent'])  # "cho thuê"
        """
        try:
            listing_types = self._data['property_attributes']['listing_type']['values']
            return {
                'sale': listing_types['sale'][lang][0],
                'rent': listing_types['rent'][lang][0]
            }
        except (KeyError, IndexError) as e:
            raise RuntimeError(
                f"Listing type display names not found for language '{lang}'. Error: {e}"
            )

    def get_listing_type_keywords(self, listing_type: str, lang: str = 'vi') -> List[str]:
        """
        Get keywords for listing type detection (sale/rent)

        Args:
            listing_type: 'sale' or 'rent'
            lang: Language code (vi/en/th/ja)

        Returns:
            List of keywords

        Example:
            sale_kw = i18n.get_listing_type_keywords('sale', 'vi')
            # ['bán', 'ban', 'cần bán', 'can ban', ...]
        """
        try:
            return self._data['property_attributes']['listing_type']['values'][listing_type][lang]
        except KeyError as e:
            raise RuntimeError(
                f"Listing type keywords not found for type='{listing_type}' lang='{lang}'. Error: {e}"
            )

    def get_ui_message(self, key: str, lang: str = 'vi') -> str:
        """
        Get UI message for specified key

        Args:
            key: Message key (e.g., 'no_results', 'error_occurred')
            lang: Language code

        Returns:
            Message string

        Example:
            msg = i18n.get_ui_message('no_results', 'vi')
            # "Xin lỗi, tôi không tìm thấy..."
        """
        try:
            return self._data['ui_messages'][lang][key]
        except KeyError as e:
            raise RuntimeError(
                f"UI message '{key}' not found for language '{lang}'. Error: {e}"
            )

    def get_price_format(self, format_key: str, lang: str = 'vi') -> str:
        """
        Get price display format

        Args:
            format_key: Format key (e.g., 'billion_format', 'negotiable')
            lang: Language code

        Returns:
            Format string

        Example:
            fmt = i18n.get_price_format('billion_format', 'vi')
            # "{value} tỷ"
        """
        try:
            return self._data['price_display'][lang][format_key]
        except KeyError as e:
            raise RuntimeError(
                f"Price format '{format_key}' not found for language '{lang}'. Error: {e}"
            )

    def format_price(self, price: float, lang: str = 'vi') -> str:
        """
        Format price according to language conventions

        Args:
            price: Price in VND
            lang: Language code

        Returns:
            Formatted price string

        Example:
            formatted = i18n.format_price(5000000000, 'vi')
            # "5.0 tỷ"
        """
        if price == 0:
            return self.get_ui_message('contact_for_price', lang)

        if price >= 1_000_000_000:
            value = price / 1_000_000_000
            fmt = self.get_price_format('billion_format', lang)
            return fmt.format(value=f"{value:.1f}")
        else:
            value = price / 1_000_000
            fmt = self.get_price_format('million_format', lang)
            return fmt.format(value=f"{value:.0f}")

    def get_possessive_keywords(self, lang: str = 'vi') -> List[str]:
        """
        Get possessive keywords for ambiguous intent detection

        Args:
            lang: Language code (vi/en/th/ja)

        Returns:
            List of possessive keywords

        Example:
            kw = i18n.get_possessive_keywords('vi')
            # ['tôi có', 'của tôi', 'nhà tôi', ...]
        """
        try:
            return self._data['possessive_keywords'][lang]
        except KeyError as e:
            raise RuntimeError(
                f"Possessive keywords not found for language '{lang}'. Error: {e}"
            )

    def get_intent_keywords(self, intent_type: str, lang: str = 'vi') -> List[str]:
        """
        Get intent keywords for intent detection

        Args:
            intent_type: Intent type (post_sale, post_rent, search_buy, search_rent, chat, etc.)
            lang: Language code (vi/en/th/ja)

        Returns:
            List of intent keywords

        Example:
            kw = i18n.get_intent_keywords('post_sale', 'vi')
            # ['bán nhà', 'bán căn hộ', 'muốn bán', ...]
        """
        try:
            return self._data['intent_keywords'][intent_type][lang]
        except KeyError as e:
            raise RuntimeError(
                f"Intent keywords not found for intent='{intent_type}' lang='{lang}'. Error: {e}"
            )

    def get_raw_data(self) -> Dict:
        """
        Get raw master data dictionary

        WARNING: Only use this if you need direct access.
        Prefer specific getter methods above.

        Returns:
            Full master data dict
        """
        return self._data


# Global singleton instance
_instance: Optional[I18nLoader] = None


def get_i18n_loader() -> I18nLoader:
    """
    Get global I18nLoader singleton instance

    Returns:
        I18nLoader instance

    Usage:
        from shared.utils.i18n_loader import get_i18n_loader

        i18n = get_i18n_loader()
        labels = i18n.get_field_labels('vi')
    """
    global _instance
    if _instance is None:
        _instance = I18nLoader()
    return _instance
