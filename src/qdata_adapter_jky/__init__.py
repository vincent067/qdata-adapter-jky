"""
qdata-adapter-jky

QDataV2 adapter for jky (吉客云开放平台)
"""

from qdata_adapter_jky.adapter import JkyAdapter
from qdata_adapter_jky.exceptions import (
    JkyAdapterError,
    JkyAdapterAuthError,
    JkyAdapterAPIError,
)

__version__ = "0.1.0"

__all__ = [
    "JkyAdapter",
    "JkyAdapterError",
    "JkyAdapterAuthError",
    "JkyAdapterAPIError",
]
