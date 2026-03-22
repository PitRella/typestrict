# must-annotate

**must-annotate** is a Python static analysis tool that **enforces the presence** of
type annotations in Python code.

Unlike mypy or pyright which verify annotation *correctness*, must-annotate simply
checks that every variable, function argument, and return value *has* an
annotation.  If it is missing — that is an error.

```python
# ERROR: missing type annotation
a = 3
result = get_user()

# OK: annotation present
a: int = 3
result: User = get_user()
```

---

## Installation

```bash
pip install must-annotate
```

Requires Python 3.10+.

---

## Usage

```bash
# Check a single file
must-annotate check app/models.py

# Check a directory recursively
must-annotate check src/

# Output as JSON (for CI/CD)
must-annotate check src/ --format json

# Check only specific rules
must-annotate check src/ --select TF001,TF002

# Exit with code 1 if errors are found (pre-commit / CI)
must-annotate check src/ --fail-on-error
```

### Example output

```
src/app/models.py:15:4  TF001  Variable 'result' missing type annotation
src/app/models.py:23:0  TF002  Argument 'user_id' missing type annotation
src/app/views.py:8:0    TF003  Function 'get_data' missing return type annotation

Found 3 errors in 2 files
```

---

## Error codes

| Code  | Description                                            | Example violation            |
|-------|--------------------------------------------------------|------------------------------|
| TF001 | Variable assignment without a type annotation          | `a = 3`                      |
| TF002 | Function argument without a type annotation            | `def f(x):`                  |
| TF003 | Function missing a return type annotation              | `def f():`                   |
| TF004 | Class attribute assigned without a type annotation     | `self.name = "test"`         |
| TF005 | Loop/context-manager variable without annotation (opt-in) | `for i in range(10):`    |

---

## Configuration (`pyproject.toml`)

```toml
[tool.must-annotate]
# Exclude directories or files from analysis
exclude = ["tests/", "migrations/", "conftest.py"]

# Disable specific rules globally
ignore = ["TF005"]

# Disable rules for specific files
per_file_ignores = { "conftest.py" = ["TF001"], "settings.py" = ["TF001"] }

# Strict mode: enables ALL rules, including TF005
strict = false
```

---

## Inline suppression

Suppress an error on a specific line:

```python
data = json.loads(response.text)  # must-annotate: ignore
```

Suppress a specific rule code:

```python
data = json.loads(response.text)  # must-annotate: ignore[TF001]
```

---

## Pre-commit integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/example/must-annotate
    rev: v0.1.0
    hooks:
      - id: must-annotate
```

---

## What is skipped automatically

- Dunder variables: `__all__`, `__version__`, etc.
- The unused-value convention: `_ = some_func()`
- Tuple unpacking: `a, b = func()` (hard to annotate inline)
- Augmented assignment: `counter += 1` (type already declared)
- `self` and `cls` as the first argument of methods

---

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type-check the library itself
mypy
```

---

## License

MIT — see [LICENSE](LICENSE).
