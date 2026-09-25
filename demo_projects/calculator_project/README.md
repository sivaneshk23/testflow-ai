# Controlled Calculator Demo

This is a small, self-created calculator project for the TestFlow AI
demonstration. It is intentionally independent from the future TestFlow AI
application and uses no network access, external services, secrets, or
personal data.

## Supported functions

`calculator.py` provides:

- `add(left, right)` — returns the sum.
- `subtract(left, right)` — returns the difference.
- `multiply(left, right)` — returns the product.
- `divide(dividend, divisor)` — divides two numbers and raises `ValueError`
  when the divisor is zero.
- `percentage(value, percent)` — validates that the percentage is between
  zero and one hundred.

All functions accept numeric values and return numeric values. The module uses
ordinary arithmetic only; it does not use `eval`, `exec`, subprocesses, or
network calls.

## Run the tests

From this directory, run:

```text
python -m pytest -q
```

The project was prepared and verified with Python 3.14.6. The command uses
the active local Python environment and does not invoke a shell command
constructed from user input.

## Intentional failure scenario

The `percentage` implementation contains one small, isolated defect: it
returns the original value instead of applying the requested percentage.
`tests/test_calculator.py::test_percentage_applies_the_requested_rate` records
the intended behavior and is marked as a strict expected failure with
`pytest.mark.xfail`.

This is deliberate demonstration data for future failure analysis. It is not
a random failure, and it does not affect the expected behavior of the other
calculator functions. The test suite should exit successfully while reporting
one expected failure (`XFAIL`) until the defect is intentionally fixed in a
future task.

