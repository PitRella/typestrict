# Fixtures for TF004 – class attributes that SHOULD trigger errors.

class BadClass:
    class_attr = "shared"  # TF004

    def __init__(self) -> None:
        self.name = "test"   # TF004
        self.value = 42      # TF004


class AnotherBad:
    count = 0              # TF004

    def __init__(self) -> None:
        self.items = []    # TF004
