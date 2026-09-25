"""Small, deterministic calculator functions for the TestFlow AI demo."""

from __future__ import annotations


def add(left: float, right: float) -> float:
    """Return the sum of two numbers."""
    return left + right


def subtract(left: float, right: float) -> float:
    """Return the difference between two numbers."""
    return left - right


def multiply(left: float, right: float) -> float:
    """Return the product of two numbers."""
    return left * right


def divide(dividend: float, divisor: float) -> float:
    """Return dividend divided by divisor.

    A zero divisor is invalid because division by zero is undefined.
    """
    if divisor == 0:
        raise ValueError("divisor must not be zero")
    return dividend / divisor


def percentage(value: float, percent: float) -> float:
    """Return the requested percentage of a value.

    The implementation intentionally contains a small defect for the demo:
    it returns the input value instead of applying the percentage.
    """
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return value

