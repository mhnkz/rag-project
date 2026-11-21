from unittest.mock import Mock

import pytest

from infrastructure.llm.openrouter_provider import (
    OpenRouterLLMProvider,
)

import httpx
from openai import APITimeoutError
from unittest.mock import patch

from openai import APIStatusError


def create_provider(client):
    return OpenRouterLLMProvider(
        api_key="test-key",
        base_url="https://example.com",
        model="test-model",
        client=client
    )


def test_generate_returns_response():
    client = Mock()

    client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(content="Hello")
            )
        ]
    )

    provider = create_provider(client)

    result = provider.generate("Hi")

    assert result == "Hello"
    client.chat.completions.create.assert_called_once()


def test_generate_sends_correct_prompt():
    client = Mock()

    client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(content="Answer")
            )
        ]
    )

    provider = create_provider(client)

    provider.generate("What is RAG?")

    client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[
            {
                "role": "user",
                "content": "What is RAG?"
            }
        ]
    )

def test_generate_retries_after_timeout():
    client = Mock()

    client.chat.completions.create.side_effect = [
        APITimeoutError(
            request=httpx.Request("POST", "https://example.com")
        ),
        Mock(
            choices=[
                Mock(
                    message=Mock(content="Success")
                )
            ]
        )
    ]

    provider = OpenRouterLLMProvider(
        api_key="test-key",
        base_url="https://example.com",
        model="test-model",
        max_retries=3,
        retry_backoff=2,
        client=client
    )

    with patch(
        "infrastructure.llm.openrouter_provider.time.sleep"
    ) as sleep_mock:

        result = provider.generate("Hello")

    assert result == "Success"
    assert client.chat.completions.create.call_count == 2
    sleep_mock.assert_called_once()


@pytest.mark.parametrize("prompt", ["", "   ", "\n"])
def test_generate_rejects_empty_prompt(prompt):
    client = Mock()

    provider = create_provider(client)

    with pytest.raises(ValueError):
        provider.generate(prompt)

    client.chat.completions.create.assert_not_called()

@pytest.mark.parametrize("status_code", [429, 503])
def test_generate_retries_after_retryable_status(status_code):
    client = Mock()

    request = httpx.Request(
        "POST",
        "https://example.com"
    )

    error_response = httpx.Response(
        status_code=status_code,
        request=request
    )

    error = APIStatusError(
        message="Temporary error",
        response=error_response,
        body=None
    )

    client.chat.completions.create.side_effect = [
        error,
        Mock(
            choices=[
                Mock(
                    message=Mock(content="Success")
                )
            ]
        )
    ]

    provider = create_provider(client)

    with patch(
        "infrastructure.llm.openrouter_provider.time.sleep"
    ) as sleep_mock:

        result = provider.generate("Hello")

    assert result == "Success"
    assert client.chat.completions.create.call_count == 2
    sleep_mock.assert_called_once()

def test_generate_does_not_retry_non_retryable_status():
    client = Mock()

    request = httpx.Request(
        "POST",
        "https://example.com"
    )

    error_response = httpx.Response(
        status_code=400,
        request=request
    )

    error = APIStatusError(
        message="Bad request",
        response=error_response,
        body=None
    )

    client.chat.completions.create.side_effect = error

    provider = create_provider(client)

    with patch(
        "infrastructure.llm.openrouter_provider.time.sleep"
    ) as sleep_mock:

        with pytest.raises(APIStatusError):
            provider.generate("Hello")

    assert client.chat.completions.create.call_count == 1
    sleep_mock.assert_not_called()