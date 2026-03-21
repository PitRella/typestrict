# Fixtures for TF002 / TF003 – functions that should NOT trigger any error.

def add(x: int, y: int) -> int:
    return x + y


def greet(name: str) -> str:
    return f"Hello, {name}"


def no_args() -> None:
    pass


async def fetch(url: str) -> bytes:
    return b""


class MyClass:
    def method(self, value: int) -> str:
        return str(value)

    @classmethod
    def create(cls, name: str) -> "MyClass":
        return cls()

    def no_extra_args(self) -> None:
        pass
