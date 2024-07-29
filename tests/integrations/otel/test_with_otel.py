from unittest.mock import MagicMock, patch

from mirascope.integrations.otel import _utils
from mirascope.integrations.otel.with_otel import with_otel


@patch(
    "mirascope.integrations.otel.with_otel.middleware_decorator",
    new_callable=MagicMock,
)
def test_with_otel(mock_middleware_decorator: MagicMock) -> None:
    """Tests the `with_otel` decorator."""
    mock_fn = MagicMock()
    with_otel(mock_fn)
    mock_middleware_decorator.assert_called_once()
    call_args = mock_middleware_decorator.call_args[1]
    assert call_args["custom_context_manager"] == _utils.custom_context_manager
    assert call_args["handle_base_model"] == _utils.handle_base_model
    assert call_args["handle_base_model_async"] == _utils.handle_base_model_async
    assert call_args["handle_call_response"] == _utils.handle_call_response
    assert call_args["handle_call_response_async"] == _utils.handle_call_response_async
    assert call_args["handle_stream"] == _utils.handle_stream
    assert call_args["handle_stream_async"] == _utils.handle_stream_async
    assert mock_middleware_decorator.call_args[0][0] == mock_fn