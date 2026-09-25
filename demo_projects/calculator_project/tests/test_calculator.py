"""Deterministic tests for the controlled calculator demo."""

import pytest

from calculator import add, divide, multiply, percentage, subtract


def test_add_returns_the_sum() -> None:
    assert add(2, 3) == 5


def test_subtract_returns_the_difference() -> None:
    assert subtract(9, 4) == 5


def test_multiply_returns_the_product() -> None:
    assert multiply(6, 7) == 42


def test_divide_returns_a_fractional_result() -> None:
    assert divide(7, 2) == 3.5


def test_divide_by_zero_is_rejected() -> None:
    with pytest.raises(ValueError, match="divisor must not be zero"):
        divide(10, 0)


def test_add_handles_zero_as_an_identity_value() -> None:
    assert add(12, 0) == 12


def test_multiply_handles_negative_values() -> None:
    assert multiply(-3, 4) == -12


def test_percentage_rejects_a_negative_percent() -> None:
    with pytest.raises(ValueError, match="percent must be between 0 and 100"):
        percentage(80, -1)


def test_percentage_rejects_a_percent_above_one_hundred() -> None:
    with pytest.raises(ValueError, match="percent must be between 0 and 100"):
        percentage(80, 101)


@pytest.mark.xfail(
    strict=True,
    reason="Known demo defect: percentage does not apply the requested rate",
)
def test_percentage_applies_the_requested_rate() -> None:
    assert percentage(200, 15) == 30

