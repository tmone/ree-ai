"""
Spam & Fraud Detection
Detect potential spam or fraudulent property listings
"""

import re
from typing import Dict, Any, Optional
from services.validation.models.validation import ValidationResult, ValidationSeverity


# Common spam keywords in Vietnamese
SPAM_KEYWORDS_VI = [
    'đảm bảo', 'chắc chắn', 'nhanh tay', 'giới hạn',
    'cơ hội duy nhất', 'không thể bỏ lỡ', 'khẩn cấp',
    'liên hệ ngay', 'số lượng có hạn', 'giá sốc',
    'siêu rẻ', 'giảm giá khủng', 'hot', 'hot hot'
]

# Spam threshold
SPAM_THRESHOLD = 50  # Score >= 50 is considered spam


def check_excessive_caps(text: str) -> tuple[int, Optional[str]]:
    """
    Check for excessive uppercase characters

    Args:
        text: Text to check

    Returns:
        (score, reason) tuple
    """
    if not text:
        return 0, None

    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

    if uppercase_ratio > 0.5:
        return 20, "Excessive uppercase in text"

    return 0, None


def check_excessive_punctuation(text: str) -> tuple[int, Optional[str]]:
    """
    Check for repeated punctuation marks

    Args:
        text: Text to check

    Returns:
        (score, reason) tuple
    """
    if not text:
        return 0, None

    if re.search(r'[!?]{3,}', text):
        return 15, "Excessive punctuation"

    return 0, None


def check_spam_keywords(text: str) -> tuple[int, Optional[str]]:
    """
    Check for common spam keywords

    Args:
        text: Text to check

    Returns:
        (score, reason) tuple
    """
    if not text:
        return 0, None

    text_lower = text.lower()
    spam_count = sum(1 for keyword in SPAM_KEYWORDS_VI if keyword in text_lower)

    if spam_count >= 3:
        return 25, f"Multiple spam keywords detected ({spam_count})"

    return 0, None


def check_zero_price(entities: Dict[str, Any]) -> tuple[int, Optional[str]]:
    """
    Check if price is zero or unrealistic

    Args:
        entities: Extracted property attributes

    Returns:
        (score, reason) tuple
    """
    price = entities.get('price', 0)

    if price == 0:
        return 30, "Price cannot be zero"

    return 0, None


def validate_spam_indicators(
    entities: Dict[str, Any],
    user_id: Optional[str] = None
) -> ValidationResult:
    """
    Detect potential spam or fraudulent listings

    Args:
        entities: Extracted property attributes
        user_id: User ID for tracking patterns

    Returns:
        ValidationResult with spam detection results
    """
    spam_score = 0
    reasons = []

    # Get title and description
    title = entities.get('title', '')
    description = entities.get('description', '')
    combined_text = f"{title} {description}"

    # Check excessive caps
    score, reason = check_excessive_caps(combined_text)
    if reason:
        spam_score += score
        reasons.append(reason)

    # Check excessive punctuation
    score, reason = check_excessive_punctuation(combined_text)
    if reason:
        spam_score += score
        reasons.append(reason)

    # Check spam keywords
    score, reason = check_spam_keywords(combined_text)
    if reason:
        spam_score += score
        reasons.append(reason)

    # Check zero price
    score, reason = check_zero_price(entities)
    if reason:
        spam_score += score
        reasons.append(reason)

    # TODO: Check duplicate phone across multiple listings
    # This requires database access - will be implemented in future iteration
    # phone = entities.get('contact_phone')
    # if phone and user_id:
    #     recent_listings = get_recent_listings_by_phone(phone, days=1)
    #     if len(recent_listings) > 10:  # More than 10 listings per day
    #         spam_score += 40
    #         reasons.append("Suspicious posting frequency")

    # Determine if spam
    is_spam = spam_score >= SPAM_THRESHOLD

    if is_spam:
        return ValidationResult(
            valid=False,
            errors=["Listing flagged as potential spam"],
            warnings=reasons,
            severity=ValidationSeverity.CRITICAL,
            metadata={'spam_score': spam_score}
        )

    if spam_score > 0:
        return ValidationResult(
            valid=True,
            warnings=reasons,
            severity=ValidationSeverity.WARNING,
            metadata={'spam_score': spam_score}
        )

    return ValidationResult(
        valid=True,
        severity=ValidationSeverity.INFO,
        metadata={'spam_score': 0}
    )
