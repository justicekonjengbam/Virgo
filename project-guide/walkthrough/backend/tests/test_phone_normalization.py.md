# backend/tests/test_phone_normalization.py

## 1. Purpose
This is a **test file** (a small program that checks that other code works. *Example:* "if I give the function `9876543210`, I expect `919876543210`"). It checks one function, `normalize_phone`, that lives in `backend/app/schemas/auth.py:4`. The test runner `pytest` finds this file and runs it. Nothing in the app imports this file.

## 2. Imports, one by one
Third-party:
- `import pytest` (`test_phone_normalization.py:1`). **pytest** is the most common Python test tool. It finds functions named `test_*` and runs them. We need it here for `pytest.mark.parametrize`. *Example of more:* `pytest.raises(ValueError)` checks that code fails the way you expect.

Project:
- `from app.schemas.auth import normalize_phone` (`:3`). This is the function under test. It comes from `backend/app/schemas/auth.py`. The `app` name works because `pyproject.toml:39` sets `pythonpath = ["."]`, so Python looks inside `backend/`.

## 3. Walk through the code
**The decorator** `@pytest.mark.parametrize('value', [...])` (`:6`).
A **decorator** (a line starting with `@` that wraps the function below it and changes how it behaves. *Example:* `@login_required` above a page function). Here, `parametrize` tells pytest: "run this test once for each item in the list, and put the item in the argument named `value`." So there are 3 test runs:
- `'9876543210'` (plain 10 digits)
- `'+91 98765 43210'` (with plus sign and spaces)
- `'919876543210'` (already has country code 91)

**The test function** `test_indian_phone_numbers_have_one_canonical_database_format(value: str) -> None` (`:7`).
- Input: one phone string. Output: nothing (`None`). A pytest test passes when it ends without an error.
- `assert normalize_phone(value) == '919876543210'` (`:8`). `assert` (stop with an error if the condition is false). `normalize_phone` removes every non-digit character, then adds `91` in front of a 10-digit number that starts with 6, 7, 8 or 9 (`app/schemas/auth.py:5-9`). All three inputs must give the same answer. "Canonical" means "one agreed single form".

Errors: if any run gives a different string, pytest shows a failed assertion with both values.

## 4. How data flows
```
pytest --reads--> this file --calls--> normalize_phone(value)
                                   |
   '+91 98765 43210' --keep digits--> '919876543210' --12 digits, starts 91--> same string
                                   |
                  assert result == '919876543210'  --> PASS or FAIL
```

## 5. Try it
```zsh
cd backend
uv run pytest tests/test_phone_normalization.py -v
```
- `uv run` runs a command inside the project's Python environment.
- `pytest` is the test runner. `-v` means verbose: print each test name.
Expected: three lines ending in `PASSED` (one per value) and `3 passed`.

## 6. Can it be better?
- Good: very short, one clear rule, three real-world formats.
- Weak: it only tests good input. There is no test for bad input such as `12345`, `5876543210` (starts with 5) or letters. `normalize_phone` raises `ValueError` for those (`auth.py:10`), but nothing checks that.
- Cleaner way (opinion):
```python
def test_bad_phone_is_rejected():
    with pytest.raises(ValueError):
        normalize_phone('5876543210')
```
- Security: none here.

## 7. Check yourself
1. How many times does pytest run the test function, and why?
2. What does `normalize_phone('+91 98765 43210')` return, and which characters get dropped?
