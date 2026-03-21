# Fixtures for TF002 / TF003 – functions that SHOULD trigger errors.

def no_return_annotation(x: int, y: int):  # TF003
    return x + y


def missing_arg_annotation(x, y: int) -> int:  # TF002
    return x + y


def fully_missing(x, y):  # TF002 TF002 TF003
    pass


async def async_no_return(value: str):  # TF003
    pass


class MyClass:
    def method_missing_arg(self, value) -> None:  # TF002
        pass

    def method_missing_return(self, value: int):  # TF003
        pass
