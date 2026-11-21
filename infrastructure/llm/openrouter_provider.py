
import random
import time

import httpx
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

from domain.rag.llm import LLMProvider


class OpenRouterLLMProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        connect_timeout: float = 10,
        read_timeout: float = 60,
        max_retries: int = 3,
        retry_backoff: float = 2,
        client=None
    ):
        if not api_key:
            raise ValueError("API key cannot be empty")

        if not base_url:
            raise ValueError("Base URL cannot be empty")

        if not model:
            raise ValueError("Model cannot be empty")

        if connect_timeout <= 0 or read_timeout <= 0:
            raise ValueError("Timeouts must be positive")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        if retry_backoff < 0:
            raise ValueError("retry_backoff cannot be negative")

        self.model = model
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        self.client = client or OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=httpx.Timeout(
                read_timeout,
                connect=connect_timeout
            ),
            max_retries=0
        )

    def _is_retryable(self, error: Exception) -> bool:
        if isinstance(
            error,
            (APIConnectionError, APITimeoutError)
        ):
            return True

        if isinstance(error, APIStatusError):
            return (
                error.status_code in (408, 409, 429)
                or error.status_code >= 500
            )

        return False

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                content = response.choices[0].message.content

                if not content:
                    raise RuntimeError(
                        "LLM returned an empty response"
                    )

                return content

            except (
                APIConnectionError,
                APITimeoutError,
                APIStatusError
            ) as error:

                if (
                    not self._is_retryable(error)
                    or attempt == self.max_retries
                ):
                    raise

                delay = (
                    self.retry_backoff * (2 ** attempt)
                    + random.uniform(0, self.retry_backoff * 0.1)
                )

                time.sleep(delay)
