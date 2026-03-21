# Fixtures for TF001 – variable assignments that SHOULD trigger errors.
# Lines marked with  # TF001  are expected to produce that error code.

a = 3                    # TF001
result = get_data()      # TF001
name = "Alice"           # TF001
items = []               # TF001
a, b = some_tuple()     # TF001 TF001

# These should NOT trigger TF001:
b: int = 5               # ok
c: str = "hello"         # ok
__version__ = "1.0.0"    # ok  – dunder
__all__ = ["a", "b"]     # ok  – dunder
_ = some_func()          # ok  – unused-value convention
data = json.loads(x)     # typestrict: ignore
typed: list[int] = []    # ok
