"""Tests the `openai.call_response_chunk` module."""

from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from openai.types.completion_usage import CompletionUsage

from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk


def test_openai_call_response_chunk() -> None:
    """Tests the `OpenAICallResponseChunk` class."""
    tool_call = ChoiceDeltaToolCall(
        index=0,
        id="id",
        function=ChoiceDeltaToolCallFunction(
            arguments='{"key": "value"}', name="function"
        ),
        type="function",
    )
    choices = [
        Choice(
            delta=ChoiceDelta(content="content", tool_calls=[tool_call]),
            index=0,
            finish_reason="stop",
        )
    ]
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    chunk = ChatCompletionChunk(
        id="id",
        choices=choices,
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
        usage=usage,
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.choices == choices
    assert call_response_chunk.choice == choices[0]
    assert call_response_chunk.delta == choices[0].delta
    assert call_response_chunk.content == "content"
    assert call_response_chunk.model == "gpt-4o"
    assert call_response_chunk.id == "id"
    assert call_response_chunk.finish_reasons == ["stop"]
    assert call_response_chunk.tool_calls == [tool_call]
    assert call_response_chunk.usage == usage
    assert call_response_chunk.input_tokens == 1
    assert call_response_chunk.output_tokens == 1


def test_openai_call_response_chunk_no_choices_or_usage() -> None:
    """Tests the `OpenAICallResponseChunk` class with None values."""
    chunk = ChatCompletionChunk(
        id="id",
        choices=[],
        created=0,
        model="gpt-4o",
        object="chat.completion.chunk",
        usage=None,
    )
    call_response_chunk = OpenAICallResponseChunk(chunk=chunk)
    assert call_response_chunk.delta is None
    assert call_response_chunk.usage is None
    assert call_response_chunk.input_tokens is None
    assert call_response_chunk.output_tokens is None
    assert call_response_chunk.tool_calls is None