# OpenAI Client Utility
import json
import logging
from typing import Dict, Any, Iterator
from openai import OpenAI
from .config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL, LOG_LEVEL

logger = logging.getLogger(__name__)


def build_system_prompt(schema: Dict[str, Any]) -> str:
    """Build system prompt with schema requirements"""
    schema_description = "You must respond with valid JSON that follows this exact schema:\n"

    for field_name, field_def in schema.items():
        schema_description += f"- {field_name}: {field_def.description} (type: {field_def.type})\n"

    schema_description += "\nIMPORTANT: Return only the JSON object, no markdown code blocks or extra text."

    return schema_description


def build_user_prompt(prompt: str, context: Dict[str, Any], pre_log_summary: str = None, user_input: str = None) -> str:
    """Build user prompt with all context information"""
    user_prompt = f"{prompt}\n\n"

    # Add context
    if context:
        user_prompt += "Current game state:\n"
        for field_name, field_value in context.items():
            description = field_value.get('description', '')
            user_prompt += f"- {field_name}: {field_value['value']} ({description})\n"
        user_prompt += "\n"

    # Add pre-log summary if provided
    if pre_log_summary:
        user_prompt += f"Recent events summary: {pre_log_summary.summary}\n"
        if pre_log_summary.recent_events:
            user_prompt += "Recent events:\n"
            for event in pre_log_summary.recent_events:
                user_prompt += f"- {event}\n"
        user_prompt += "\n"

    # Add user input if provided
    if user_input:
        user_prompt += f"User action: {user_input}\n\n"

    return user_prompt


def generate_structured(
    prompt: str,
    context: Dict[str, Any],
    schema: Dict[str, Any],
    pre_log_summary: str = None,
    user_input: str = None,
    model: str = None,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Generate structured output using OpenAI API

    Args:
        prompt: The prompt for generation
        context: Current game context
        schema: Output schema definition
        pre_log_summary: Historical events summary
        user_input: User's current input
        model: Override model (defaults to config model)
        stream: Whether to use streaming

    Returns:
        Dict with generated structured data
    """
    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    model = model or OPENAI_MODEL

    system_prompt = build_system_prompt(schema)
    user_prompt = build_user_prompt(prompt, context, pre_log_summary, user_input)

    logger.debug(f"System prompt: {system_prompt}")
    logger.debug(f"User prompt: {user_prompt}")

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    if stream:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )

        content = response.choices[0].message.content
        logger.debug(f"Raw response: {content}")

        # Try to parse JSON from response
        try:
            # Remove any markdown code blocks if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)
            logger.debug(f"Parsed result: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content}")
            raise ValueError(f"Invalid JSON response: {e}")