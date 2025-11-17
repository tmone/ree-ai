"""
Multilingual Keywords Manager
Loads and manages keywords from master data file for intent detection,
confirmation, and other NLP tasks.
"""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class MultilingualKeywords:
    """
    Manages multilingual keywords from master data file.

    Features:
    - Load keywords from JSON master data
    - Access keywords by category and language
    - Cache for performance
    - Reload capability
    """

    _instance = None  # Singleton instance
    _keywords_data = None

    def __new__(cls):
        """Singleton pattern to avoid loading file multiple times"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize and load keywords if not already loaded"""
        if self._keywords_data is None:
            self.load_keywords()

    def load_keywords(self, filepath: Optional[str] = None):
        """
        Load keywords from JSON file.

        Args:
            filepath: Optional custom file path. If None, uses default location.
        """
        if filepath is None:
            # Default: shared/data/multilingual_keywords.json
            current_dir = Path(__file__).parent
            filepath = current_dir.parent / 'data' / 'multilingual_keywords.json'

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self._keywords_data = json.load(f)
            print(f"✅ Loaded multilingual keywords v{self._keywords_data.get('version', 'unknown')}")
        except FileNotFoundError:
            print(f"❌ Keywords file not found: {filepath}")
            self._keywords_data = {}
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse keywords JSON: {e}")
            self._keywords_data = {}

    def get_confirmation_keywords(self, languages: Optional[List[str]] = None) -> List[str]:
        """
        Get confirmation keywords for specified languages.

        Args:
            languages: List of language codes (e.g., ['vi', 'en']). If None, returns all.

        Returns:
            List of confirmation keywords
        """
        if not self._keywords_data:
            return []

        confirmation = self._keywords_data.get('confirmation_keywords', {})

        if languages is None:
            # Return all languages
            all_keywords = []
            for lang, keywords in confirmation.items():
                if lang != 'description' and isinstance(keywords, list):
                    all_keywords.extend(keywords)
            return all_keywords
        else:
            # Return specific languages
            keywords = []
            for lang in languages:
                keywords.extend(confirmation.get(lang, []))
            return keywords

    def get_intent_keywords(self, intent: str, languages: Optional[List[str]] = None) -> List[str]:
        """
        Get keywords for specific intent.

        Args:
            intent: Intent name (e.g., 'post_sale', 'search_buy')
            languages: List of language codes. If None, returns all.

        Returns:
            List of keywords for the intent
        """
        if not self._keywords_data:
            return []

        intent_keywords = self._keywords_data.get('intent_keywords', {}).get(intent, {})

        if languages is None:
            # Return all languages
            all_keywords = []
            for lang, keywords in intent_keywords.items():
                if lang != 'description' and isinstance(keywords, list):
                    all_keywords.extend(keywords)
            return all_keywords
        else:
            # Return specific languages
            keywords = []
            for lang in languages:
                keywords.extend(intent_keywords.get(lang, []))
            return keywords

    def get_property_type_keywords(self, property_type: str, languages: Optional[List[str]] = None) -> List[str]:
        """
        Get keywords for property type.

        Args:
            property_type: Property type (e.g., 'apartment', 'villa')
            languages: List of language codes. If None, returns all.

        Returns:
            List of keywords for the property type
        """
        if not self._keywords_data:
            return []

        property_types = self._keywords_data.get('property_types', {})

        if languages is None:
            # Return all languages
            all_keywords = []
            for lang, types in property_types.items():
                if lang != 'description' and isinstance(types, dict):
                    all_keywords.extend(types.get(property_type, []))
            return all_keywords
        else:
            # Return specific languages
            keywords = []
            for lang in languages:
                lang_types = property_types.get(lang, {})
                keywords.extend(lang_types.get(property_type, []))
            return keywords

    def get_missing_info_prompt(self, field: str, language: str = 'vi') -> str:
        """
        Get prompt text for missing information.

        Args:
            field: Field name (e.g., 'title', 'description')
            language: Language code (default: 'vi')

        Returns:
            Prompt text for the field
        """
        if not self._keywords_data:
            return f"Please provide {field}"

        prompts = self._keywords_data.get('missing_info_prompts', {})
        lang_prompts = prompts.get(language, {})
        return lang_prompts.get(field, f"Please provide {field}")

    def get_frustration_keywords(self, languages: Optional[List[str]] = None) -> List[str]:
        """
        Get frustration keywords for specified languages.

        Args:
            languages: List of language codes (e.g., ['vi', 'en']). If None, returns all.

        Returns:
            List of frustration keywords
        """
        if not self._keywords_data:
            return []

        frustration = self._keywords_data.get('frustration_keywords', {})

        if languages is None:
            # Return all languages
            all_keywords = []
            for lang, keywords in frustration.items():
                if lang != 'description' and isinstance(keywords, list):
                    all_keywords.extend(keywords)
            return all_keywords
        else:
            # Return specific languages
            keywords = []
            for lang in languages:
                keywords.extend(frustration.get(lang, []))
            return keywords

    def get_all_data(self) -> Dict:
        """Get all keywords data"""
        return self._keywords_data or {}

    def reload(self):
        """Reload keywords from file"""
        self._keywords_data = None
        self.load_keywords()


# Singleton instance for easy import
keywords_manager = MultilingualKeywords()


# Convenience functions
def get_confirmation_keywords(languages: Optional[List[str]] = None) -> List[str]:
    """Get confirmation keywords"""
    return keywords_manager.get_confirmation_keywords(languages)


def get_intent_keywords(intent: str, languages: Optional[List[str]] = None) -> List[str]:
    """Get intent keywords"""
    return keywords_manager.get_intent_keywords(intent, languages)


def get_property_type_keywords(property_type: str, languages: Optional[List[str]] = None) -> List[str]:
    """Get property type keywords"""
    return keywords_manager.get_property_type_keywords(property_type, languages)


def get_missing_info_prompt(field: str, language: str = 'vi') -> str:
    """Get missing info prompt"""
    return keywords_manager.get_missing_info_prompt(field, language)


def get_frustration_keywords(languages: Optional[List[str]] = None) -> List[str]:
    """Get frustration keywords"""
    return keywords_manager.get_frustration_keywords(languages)
