# OpenAI Proxy
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .config import OPENAI_BASE_URL, OPENAI_API_KEY


def complete(
    messages: List[Dict[str, str]],
    model: str,
    max_tokens: int,
    response_format: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Complete using OpenAI API (non-streaming)
    """
    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

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
    response_format: Optional[Dict[str, str]] = None
):
    """
    Complete using OpenAI API (streaming)
    """
    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

    return client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        response_format=response_format,
        stream=True
    )
