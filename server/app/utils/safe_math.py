"""
Safe Math Utilities
-------------------
Production-grade mathematical operations with zero-division protection.

DESIGN PRINCIPLES:
- Every division operation has explicit zero-guard
- Fallback values are documented and logged
- No runtime math exceptions can escape
- Reason codes explain every fallback
"""

from typing import List, Optional, Tuple
from .logger import logger


class MathFallbackReason:
    """Reason codes for fallback decisions (for explainability)."""
    DENOMINATOR_ZERO = "DENOMINATOR_ZERO"
    EMPTY_ARRAY = "EMPTY_ARRAY"
    ALL_WEIGHTS_ZERO = "ALL_WEIGHTS_ZERO"
    NO_VALID_VALUES = "NO_VALID_VALUES"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    OVERFLOW_PROTECTION = "OVERFLOW_PROTECTION"
    NORMALIZATION_FALLBACK = "NORMALIZATION_FALLBACK"


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
    log_warning: bool = True,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Safe division with zero-guard.
    
    Args:
        numerator: The dividend
        denominator: The divisor
        default: Value to return if denominator is zero
        log_warning: Whether to log when fallback is used
        context: Description of where this division occurs (for logging)
    
    Returns:
        Tuple of (result, reason_code) where reason_code is None if division succeeded
    
    Example:
        result, reason = safe_divide(100, count, default=0, context="avg calculation")
        if reason:
            risk_factors.append({"reason": reason, "description": "Used fallback"})
    """
    if denominator == 0:
        if log_warning:
            logger.warning(
                f"Division by zero avoided: {numerator}/{denominator} -> {default} "
                f"[context: {context or 'unspecified'}]"
            )
        return default, MathFallbackReason.DENOMINATOR_ZERO
    
    try:
        result = numerator / denominator
        return result, None
    except (ZeroDivisionError, FloatingPointError) as e:
        logger.error(f"Unexpected math error in safe_divide: {e} [context: {context}]")
        return default, MathFallbackReason.DENOMINATOR_ZERO


def safe_average(
    values: List[float],
    default: float = 0.0,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Safe average calculation with empty-array protection.
    
    Args:
        values: List of values to average
        default: Value to return if list is empty
        context: Description for logging
    
    Returns:
        Tuple of (average, reason_code)
    """
    if not values:
        logger.warning(f"Empty array in average calculation -> {default} [context: {context}]")
        return default, MathFallbackReason.EMPTY_ARRAY
    
    return safe_divide(sum(values), len(values), default, context=context)


def safe_weighted_average(
    values: List[float],
    weights: List[float],
    default: float = 0.0,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Safe weighted average with zero-weight and empty-array protection.
    
    Args:
        values: List of values
        weights: Corresponding weights
        default: Fallback value
        context: Description for logging
    
    Returns:
        Tuple of (weighted_average, reason_code)
    """
    if not values or not weights:
        logger.warning(f"Empty arrays in weighted average -> {default} [context: {context}]")
        return default, MathFallbackReason.EMPTY_ARRAY
    
    if len(values) != len(weights):
        logger.error(f"Mismatched array lengths: values={len(values)}, weights={len(weights)}")
        return default, MathFallbackReason.NO_VALID_VALUES
    
    total_weight = sum(weights)
    if total_weight == 0:
        logger.warning(f"All weights are zero -> {default} [context: {context}]")
        return default, MathFallbackReason.ALL_WEIGHTS_ZERO
    
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return safe_divide(weighted_sum, total_weight, default, context=context)


def safe_normalize(
    value: float,
    min_val: float,
    max_val: float,
    default: float = 0.0,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Safe min-max normalization to 0-1 range.
    
    Args:
        value: Value to normalize
        min_val: Minimum of range
        max_val: Maximum of range
        default: Fallback if range is zero
        context: Description for logging
    
    Returns:
        Tuple of (normalized_value, reason_code)
    """
    range_size = max_val - min_val
    if range_size == 0:
        logger.warning(f"Zero range in normalization [{min_val}, {max_val}] -> {default} [context: {context}]")
        return default, MathFallbackReason.NORMALIZATION_FALLBACK
    
    normalized = (value - min_val) / range_size
    # Clamp to 0-1
    return max(0.0, min(1.0, normalized)), None


def safe_percentage(
    part: float,
    whole: float,
    default: float = 0.0,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Safe percentage calculation (part/whole * 100).
    
    Returns:
        Tuple of (percentage, reason_code)
    """
    result, reason = safe_divide(part, whole, default=default / 100, context=context)
    if reason:
        return default, reason
    return result * 100, None


def safe_clamp(
    value: float,
    min_val: float = 0.0,
    max_val: float = 100.0
) -> float:
    """
    Clamp value to range. No exceptions possible.
    """
    return max(min_val, min(max_val, value))


def safe_risk_score(
    raw_score: float,
    min_score: float = 0.0,
    max_score: float = 100.0,
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Ensure risk score is valid and within bounds.
    
    Returns:
        Tuple of (clamped_score, reason_code if adjustment was made)
    """
    reason = None
    
    if raw_score < min_score:
        logger.warning(f"Risk score {raw_score} below minimum, clamping to {min_score} [context: {context}]")
        raw_score = min_score
        reason = MathFallbackReason.NEGATIVE_VALUE
    elif raw_score > max_score:
        logger.warning(f"Risk score {raw_score} above maximum, clamping to {max_score} [context: {context}]")
        raw_score = max_score
        reason = MathFallbackReason.OVERFLOW_PROTECTION
    
    return raw_score, reason


def calculate_confidence(
    component_scores: List[float],
    component_weights: List[float],
    context: str = ""
) -> Tuple[float, Optional[str]]:
    """
    Calculate confidence score with full safety guards.
    
    Confidence is based on:
    - Having sufficient data points
    - Consistency of readings
    - Total weight of contributing factors
    
    Returns:
        Tuple of (confidence 0-1, reason_code)
    """
    if not component_scores:
        logger.warning(f"No component scores for confidence -> 0.5 [context: {context}]")
        return 0.5, MathFallbackReason.EMPTY_ARRAY
    
    # Base confidence from having data
    base_confidence = min(1.0, len(component_scores) / 3)  # 3+ components = full base
    
    # Weight contribution
    total_weight = sum(component_weights) if component_weights else 0
    weight_factor, _ = safe_divide(total_weight, 100, default=0.5, context=f"{context}_weight")
    weight_factor = min(1.0, weight_factor)
    
    # Combined confidence
    confidence = (base_confidence + weight_factor) / 2
    return safe_clamp(confidence, 0.0, 1.0), None
