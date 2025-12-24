# OpenAI Client Utility
import json
import logging
from typing import Dict, Any, Iterator
from openai import OpenAI
from .config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL, LOG_LEVEL, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)


def build_system_prompt(schema: Dict[str, Any]) -> str:
    """Build system prompt with schema requirements"""
    schema_description = "You must respond with ONLY valid JSON that follows this exact schema:\n"

    for field_name, field_def in schema.items():
        schema_description += f"- {field_name}: {field_def.description} (type: {field_def.type})\n"

    schema_description += """
CRITICAL RULES:
1. Return ONLY the JSON object, nothing else
2. NO thinking process, NO explanations, NO markdown
3. Ensure all JSON strings are properly closed with quotes
4. Do NOT use control characters or special symbols in strings
5. Your entire response must be valid JSON starting with opening brace and ending with closing brace
"""

    return schema_description


def build_user_prompt(prompt: str, context: Dict[str, Any], pre_log_summary: str = None, user_input: str = None) -> str:
    """Build user prompt with all context information"""
    user_prompt = f"{prompt}\n\n"

    # Add context
    if context:
        user_prompt += "Current game state:\n"
        for field_name, field_value in context.items():
            # Handle both dict and Pydantic model
            if isinstance(field_value, dict):
                value = field_value.get('value', '')
                description = field_value.get('description', '')
            else:
                # Pydantic model or object with attributes
                value = getattr(field_value, 'value', '')
                description = getattr(field_value, 'description', '')

            user_prompt += f"- {field_name}: {value} ({description})\n"
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
    logger.info(f"Calling OpenAI with model={model}, max_tokens={LLM_MAX_TOKENS}")

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    if stream:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=LLM_MAX_TOKENS,
            response_format={"type": "json_object"},
            stream=True
        )
    else:
        # Create completion without streaming
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=LLM_MAX_TOKENS,
            response_format={"type": "json_object"},
            stream=False
        )

        # Extract content from the completion
        if not hasattr(completion, 'choices') or len(completion.choices) == 0:
            logger.error(f"Invalid response structure: {completion}")
            raise ValueError("Invalid response structure from OpenAI API")

        message = completion.choices[0].message
        content = getattr(message, 'content', '')
        reasoning_content = getattr(message, 'reasoning_content', '')

        logger.debug(f"Reasoning content: {reasoning_content}")
        logger.debug(f"Main content: {content}")

        # Use content field for JSON parsing, ignore reasoning_content
        if not content:
            raise ValueError("No content received from OpenAI API")

        # Try to parse JSON from response with adaptive extraction
        def extract_json_from_text(text: str) -> str:
            """Extract JSON from mixed content (thoughts + JSON)"""
            text = text.strip()

            # Method 1: Find JSON code blocks
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                if end != -1:
                    return text[start:end].strip()
            elif '```' in text:
                start = text.find('```') + 3
                end = text.find('```', start)
                if end != -1:
                    return text[start:end].strip()

            # Method 2: Find JSON object boundaries
            json_start = -1
            brace_count = 0
            in_string = False
            escape_next = False

            for i, char in enumerate(text):
                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == '{':
                        if json_start == -1:
                            json_start = i
                        brace_count += 1
                    elif char == '}':
                        if json_start != -1:
                            brace_count -= 1
                            if brace_count == 0:
                                return text[json_start:i+1]

            # Method 3: Try to find simple JSON patterns
            lines = text.split('\n')
            json_lines = []
            in_json = False

            for line in lines:
                line = line.strip()
                if line.startswith('{'):
                    in_json = True
                    json_lines.append(line)
                elif in_json:
                    json_lines.append(line)
                    if line.endswith('}'):
                        break

            if json_lines:
                potential_json = '\n'.join(json_lines)
                try:
                    json.loads(potential_json)
                    return potential_json
                except:
                    pass

            # Method 4: Try the whole text as last resort
            return text

        def clean_json_string(json_str: str) -> str:
            """Clean JSON string by removing/escaping control characters"""
            import re
            # Remove control characters except \n, \r, \t
            # Control chars are 0x00-0x1F except tab(0x09), newline(0x0A), carriage return(0x0D)
            cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', json_str)
            return cleaned

        try:
            # Strategy 1: Try to extract from content first (most reliable)
            json_content = extract_json_from_text(content)
            logger.debug(f"Extracted JSON from content: {json_content[:200]}...")

            # Validate it's actually JSON-like (starts with { or [)
            json_content_stripped = json_content.strip()
            if not json_content_stripped.startswith('{') and not json_content_stripped.startswith('['):
                logger.warning("Extracted content doesn't look like JSON, trying with reasoning...")
                # Strategy 2: If content extraction failed, try full text including reasoning
                if reasoning_content:
                    full_text = f"{reasoning_content}\n\n{content}"
                    json_content = extract_json_from_text(full_text)
                    logger.debug(f"Extracted JSON from full text: {json_content[:200]}...")

            # Clean control characters
            json_content_cleaned = clean_json_string(json_content)
            if json_content != json_content_cleaned:
                logger.warning("Control characters found and removed from JSON")
                logger.debug(f"Cleaned JSON content: {json_content_cleaned[:200]}...")

            result = json.loads(json_content_cleaned)
            logger.debug(f"Parsed result: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Extracted JSON content: {json_content if 'json_content' in locals() else 'N/A'}")
            logger.error(f"Full content: {content[:500]}...")
            logger.error(f"Reasoning content: {reasoning_content[:500] if reasoning_content else 'N/A'}")
            raise ValueError(f"Invalid JSON response: {e}")