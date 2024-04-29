"""Integration with Logfire from Pydantic"""
from functools import wraps
from typing import Callable, Optional, overload

import logfire
from pydantic import BaseModel

from mirascope.base.types import BaseCallResponseChunk, ChunkT

from ..types import (
    BaseCallT,
    BaseChunkerT,
    BaseEmbedderT,
    BaseExtractorT,
    BaseVectorStoreT,
)


def mirascope_span(fn: Callable):
    """Wraps a pydantic class method with a Logfire span."""

    @wraps(fn)
    def wrapper(self: BaseModel, *args, **kwargs):
        class_vars = {}
        for classvars in self.__class_vars__:
            if not classvars == "api_key":
                class_vars[classvars] = getattr(self.__class__, classvars)
        with logfire.span(
            f"{self.__class__.__name__}.{fn.__name__}",
            class_vars=class_vars,
            *args,
            **kwargs,
        ) as logfire_span:
            result = fn(self, *args, **kwargs)
            logfire_span.set_attribute("response", result)
            return result

    return wrapper


def mirascope_logfire(
    fn: Callable,
    suffix: str,
    response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
) -> Callable:
    """Wraps a function with a Logfire span."""
    return (
        mirascope_stream(fn, suffix, response_chunk_type)
        if response_chunk_type
        else mirascope_create(fn, suffix)
    )


async def mirascope_logfire_async(
    fn: Callable,
    suffix: str,
    response_chunk_type: Optional[type[BaseCallResponseChunk]] = None,
) -> Callable:
    """Wraps an asynchronous function with a Logfire span."""
    return await (
        mirascope_stream_async(fn, suffix, response_chunk_type)
        if response_chunk_type
        else mirascope_create_async(fn, suffix)
    )


def mirascope_create(fn: Callable, suffix: str) -> Callable:
    """Wraps a function with a Logfire span."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        span_data = {
            "async": False,
            "request_data": kwargs,
        }
        model = kwargs.get("model", "unknown")
        with logfire.with_settings(custom_scope_suffix=suffix).span(
            f"{suffix}.{fn.__name__} with {model}", **span_data
        ) as logfire_span:
            result = fn(*args, **kwargs)
            logfire_span.set_attribute("response_data", result)
            return result

    return wrapper


def extract_chunk_content(
    chunk: ChunkT, response_chunk_type: type[BaseCallResponseChunk]
) -> Optional[str]:
    """Extracts the content from a chunk."""
    chunk_content = response_chunk_type(chunk=chunk).content
    if chunk_content is not None:
        return chunk_content
    return None


def mirascope_stream(
    fn: Callable, suffix: str, response_chunk_type: type[BaseCallResponseChunk]
) -> Callable:
    """Wraps a function that yields a generator with a Logfire span."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        span_data = {
            "async": False,
            "request_data": kwargs,
        }
        model = kwargs.get("model", "unknown")
        with logfire.with_settings(custom_scope_suffix=suffix).span(
            f"{suffix}.{fn.__name__} with {model}", **span_data
        ) as logfire_span:
            content = []
            stream = fn(*args, **kwargs)
            if suffix != "anthropic":
                for chunk in stream:
                    chunk_content = extract_chunk_content(chunk, response_chunk_type)
                    if chunk_content:
                        content.append(chunk_content)
                    yield chunk
            else:
                with stream as s:
                    for chunk in s:
                        chunk_content = extract_chunk_content(
                            chunk, response_chunk_type
                        )
                        if chunk_content:
                            content.append(chunk_content)
                        yield chunk
            logfire_span.set_attribute(
                "response_data",
                {
                    "combined_chunk_content": "".join(content),
                    "chunk_count": len(content),
                },
            )

    return wrapper


async def mirascope_create_async(fn: Callable, suffix: str) -> Callable:
    """Wraps a asynchronous function that yields a generator with a Logfire span."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        span_data = {
            "async": True,
            "request_data": kwargs,
        }
        model = kwargs.get("model", "unknown")
        with logfire.with_settings(custom_scope_suffix=suffix).span(
            f"{suffix}.{fn.__name__} with {model}", **span_data
        ) as logfire_span:
            result = await fn(*args, **kwargs)
            logfire_span.set_attribute("response_data", result)
            return result

    return wrapper


async def mirascope_stream_async(
    fn: Callable, suffix: str, response_chunk_type: type[BaseCallResponseChunk]
) -> Callable:
    """Wraps an asynchronous function with a Logfire span."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        span_data = {
            "async": True,
            "request_data": kwargs,
        }
        model = kwargs.get("model", "unknown")
        with logfire.with_settings(custom_scope_suffix=suffix).span(
            f"{suffix}.{fn.__name__} with {model}", **span_data
        ) as logfire_span:
            content = []
            stream = await fn(*args, **kwargs)
            if suffix != "anthropic":
                async for chunk in stream:
                    chunk_content = extract_chunk_content(chunk, response_chunk_type)
                    if chunk_content:
                        content.append(chunk_content)
                    yield chunk
            else:
                async with stream as s:
                    async for chunk in s:
                        chunk_content = extract_chunk_content(
                            chunk, response_chunk_type
                        )
                        if chunk_content:
                            content.append(chunk_content)
                        yield chunk
            logfire_span.set_attribute(
                "response_data",
                {
                    "combined_chunk_content": "".join(content),
                    "chunk_count": len(content),
                },
            )

    return wrapper


def get_parent_class_name(cls: type[BaseModel], target_name: str) -> Optional[str]:
    """Recursively searches for a parent class with a given name."""
    for base in cls.__bases__:
        if base.__name__.startswith(target_name):
            return base.__name__
        else:
            parent_name = get_parent_class_name(base, target_name)
            if parent_name:
                return parent_name
    return None


@overload
def with_logfire(cls: type[BaseCallT]) -> type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseExtractorT]) -> type[BaseExtractorT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseVectorStoreT]) -> type[BaseVectorStoreT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseChunkerT]) -> type[BaseChunkerT]:
    ...  # pragma: no cover


@overload
def with_logfire(cls: type[BaseEmbedderT]) -> type[BaseEmbedderT]:
    ...  # pragma: no cover


def with_logfire(cls):
    """Wraps a pydantic class with a Logfire span."""
    if hasattr(cls, "call"):
        setattr(cls, "call", mirascope_span(cls.call))
    if hasattr(cls, "stream"):
        setattr(cls, "stream", mirascope_span(cls.stream))
    if hasattr(cls, "call_async"):
        setattr(cls, "call_async", mirascope_span(cls.call_async))
    if hasattr(cls, "stream_async"):
        setattr(cls, "stream_async", mirascope_span(cls.stream_async))
    if hasattr(cls, "extract"):
        setattr(cls, "extract", mirascope_span(cls.extract))
    if hasattr(cls, "extract_async"):
        setattr(cls, "extract_async", mirascope_span(cls.extract_async))
    if get_parent_class_name(cls, "OpenAI"):
        if hasattr(cls, "call_params"):
            cls.call_params.logfire = logfire.instrument_openai
        if hasattr(cls, "embedding_params"):
            cls.embedding_params.logfire = mirascope_logfire
    else:
        if hasattr(cls, "call_params"):
            cls.call_params.logfire = mirascope_logfire
            cls.call_params.logfire_async = mirascope_logfire_async
        if hasattr(cls, "vectorstore_params"):
            cls.vectorstore_params.logfire = mirascope_span
            cls.vectorstore_params.logfire_async = mirascope_span
    return cls
