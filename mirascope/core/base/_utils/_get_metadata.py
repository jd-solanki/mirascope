"""Utility for pulling metadata from a call and merging with any dynamic metadata."""

from typing import Callable

from ..dynamic_config import BaseDynamicConfig
from ..metadata import Metadata


def get_metadata(fn: Callable, dynamic_config: BaseDynamicConfig) -> Metadata:
    """Get the metadata from the function and merge with any dynamic metadata."""
    if dynamic_config and "metadata" in dynamic_config:
        return dynamic_config["metadata"]
    return fn.__annotations__.get("metadata", {})