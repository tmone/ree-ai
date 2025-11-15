"""
Language Detection Service
Auto-detect language from user input text
"""
from typing import Optional
from langdetect import detect, LangDetectException
from shared.utils.logger import setup_logger, LogEmoji


class LanguageDetector:
    """
    Detect language from input text using langdetect library
    """

    # Supported languages
    SUPPORTED_LANGUAGES = {'vi', 'en', 'zh-cn', 'ko', 'ja'}

    def __init__(self):
        self.logger = setup_logger("language_detector")

    def detect_language(self, text: str) -> str:
        """
        Detect language from text

        Args:
            text: Input text to analyze

        Returns:
            Language code: 'vi', 'en', 'zh', 'ko', 'ja'
            Defaults to 'en' if detection fails
        """
        if not text or not text.strip():
            return 'en'  # Default to English

        try:
            detected = detect(text)

            # Map langdetect codes to our supported codes
            lang_mapping = {
                'vi': 'vi',
                'en': 'en',
                'zh-cn': 'zh',
                'zh-tw': 'zh',
                'ko': 'ko',
                'ja': 'ja'
            }

            lang_code = lang_mapping.get(detected, 'en')

            # Verify it's in our supported list
            if lang_code not in self.SUPPORTED_LANGUAGES:
                self.logger.warning(
                    f"{LogEmoji.WARNING} Detected language '{detected}' not supported, "
                    f"defaulting to 'en'"
                )
                return 'en'

            self.logger.info(
                f"{LogEmoji.SUCCESS} Detected language: {lang_code} (raw: {detected})"
            )
            return lang_code

        except LangDetectException as e:
            self.logger.warning(
                f"{LogEmoji.WARNING} Language detection failed: {e}, defaulting to 'en'"
            )
            return 'en'

    def detect_with_confidence(self, text: str) -> tuple[str, float]:
        """
        Detect language with confidence score

        Args:
            text: Input text

        Returns:
            Tuple of (language_code, confidence)
        """
        try:
            from langdetect import detect_langs

            if not text or not text.strip():
                return ('en', 0.5)

            results = detect_langs(text)

            if not results:
                return ('en', 0.5)

            # Get top result
            top_result = results[0]
            detected_lang = top_result.lang
            confidence = top_result.prob

            # Map to our codes
            lang_mapping = {
                'vi': 'vi',
                'en': 'en',
                'zh-cn': 'zh',
                'zh-tw': 'zh',
                'ko': 'ko',
                'ja': 'ja'
            }

            lang_code = lang_mapping.get(detected_lang, 'en')

            self.logger.info(
                f"{LogEmoji.SUCCESS} Language detection: {lang_code} "
                f"(confidence: {confidence:.2f})"
            )

            return (lang_code, confidence)

        except Exception as e:
            self.logger.warning(
                f"{LogEmoji.WARNING} Language detection failed: {e}"
            )
            return ('en', 0.5)

    def is_vietnamese(self, text: str) -> bool:
        """
        Quick check if text is Vietnamese

        Args:
            text: Input text

        Returns:
            True if Vietnamese
        """
        # Check for Vietnamese diacritics
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'

        if not text:
            return False

        # If contains Vietnamese chars, likely Vietnamese
        text_lower = text.lower()
        has_vietnamese_chars = any(char in text_lower for char in vietnamese_chars)

        if has_vietnamese_chars:
            return True

        # Otherwise, use langdetect
        detected = self.detect_language(text)
        return detected == 'vi'

    def normalize_language_code(self, lang_code: Optional[str]) -> str:
        """
        Normalize language code to supported format

        Args:
            lang_code: Input language code (can be 'vi', 'vie', 'vietnamese', etc.)

        Returns:
            Normalized code: 'vi', 'en', 'zh', 'ko', 'ja'
        """
        if not lang_code:
            return 'en'

        lang_code = lang_code.lower().strip()

        # Direct mapping
        mapping = {
            'vi': 'vi',
            'vie': 'vi',
            'vietnamese': 'vi',
            'tiếng việt': 'vi',
            'en': 'en',
            'eng': 'en',
            'english': 'en',
            'zh': 'zh',
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'chinese': 'zh',
            '中文': 'zh',
            'ko': 'ko',
            'kor': 'ko',
            'korean': 'ko',
            '한국어': 'ko',
            'ja': 'ja',
            'jpn': 'ja',
            'japanese': 'ja',
            '日本語': 'ja'
        }

        return mapping.get(lang_code, 'en')
