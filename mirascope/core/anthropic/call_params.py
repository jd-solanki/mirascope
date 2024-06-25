"""The parameters to use when calling the Anthropic API."""

from __future__ import annotations

from typing import Literal

from anthropic.types.completion_create_params import Metadata
from httpx import Timeout
from typing_extensions import NotRequired, Required

from ..base import BaseCallParams


class AnthropicCallParams(BaseCallParams):
    """The parameters to use when calling the Anthropic API."""

    max_tokens: Required[int]
    metadata: NotRequired[Metadata | None]
    stop_sequences: NotRequired[list[str] | None]
    system: NotRequired[str | None]
    temperature: NotRequired[float | None]
    top_k: NotRequired[int | None]
    top_p: NotRequired[float | None]
    timeout: NotRequired[float | Timeout | None]

    response_format: NotRequired[Literal["json"] | None]
