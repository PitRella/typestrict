"""typeforce – enforce type annotation presence in Python code."""
from typeforce.checker import check_file, check_source
from typeforce.config import TypeforceConfig, load_config
from typeforce.errors import TypeforceError

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "TypeforceError",
    "TypeforceConfig",
    "load_config",
    "check_source",
    "check_file",
]
