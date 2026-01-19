# OpenAI Proxy
from typing import List, Dict, Any, Optional
from .client_pool import client_pool


def complete(
    messages: List[Dict[str, str]],
    model: str,
    max_tokens: int,
    base_url: str,
    api_key: str,
    response_format: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Complete using OpenAI API (non-streaming)
    """
    client = client_pool.get_client(base_url, api_key)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        response_format=response_format,
        stream=False
    )

    if not hasattr(completion, 'choices') or len(completion.choices) == 0:
        raise ValueError("Invalid response structure from OpenAI API")

    message = completion.choices[0].message
    content = getattr(message, 'content', '')
    reasoning_content = getattr(message, 'reasoning_content', '')

    return {
        'content': content,
        'reasoning_content': reasoning_content
    }


def complete_stream(
    messages: List[Dict[str, str]],
    model: str,
    max_tokens: int,
    base_url: str,
    api_key: str,
    response_format: Optional[Dict[str, str]] = None
):
    """
    Complete using OpenAI API (streaming)
    """
    client = client_pool.get_client(base_url, api_key)

    return client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        response_format=response_format,
        stream=True
    )
