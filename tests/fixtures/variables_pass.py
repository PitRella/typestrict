# Fixtures for TF001 – variable assignments that should NOT trigger any error.

x: int = 1
y: str = "hello"
z: list[int] = [1, 2, 3]
mapping: dict[str, int] = {}

__version__: str = "0.1.0"
__all__ = ["x", "y"]          # dunder – skip
_ = some_call()               # unused-value convention – skip

counter: int = 0
counter += 1                  # AugAssign – not an ast.Assign
