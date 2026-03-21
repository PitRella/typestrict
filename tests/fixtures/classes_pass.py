# Fixtures for TF004 – class attributes that should NOT trigger any error.

class GoodClass:
    class_attr: str = "shared"
    count: int = 0

    def __init__(self) -> None:
        self.name: str = "test"
        self.value: int = 42
        self.items: list[str] = []


class DataClass:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
