"""Test client for OpenAI LLM Service"""

import httpx
import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMTestClient:
    """Test client for OpenAI LLM Service"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=60.0)

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            response = self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise

    def generate_structured(
        self,
        prompt: str,
        context: Dict[str, Any],
        schema: Dict[str, Any],
        pre_log_summary: Dict[str, Any] = None,
        user_input: str = None,
        stream: bool = False,
        model: str = None
    ) -> Dict[str, Any]:
        """Generate structured data"""
        request_data = {
            "prompt": prompt,
            "context": context,
            "schema": schema,
            "stream": stream
        }

        if pre_log_summary:
            request_data["pre_log_summary"] = pre_log_summary
        if user_input:
            request_data["user_input"] = user_input
        if model:
            request_data["model"] = model

        try:
            response = self.client.post(
                f"{self.base_url}/generate_structured",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise

    def generate_structured_stream(self, request_data: Dict[str, Any]) -> List[str]:
        """Generate structured data with streaming"""
        try:
            response = self.client.post(
                f"{self.base_url}/generate_structured_stream",
                json=request_data
            )
            response.raise_for_status()

            # Read streaming response
            chunks = []
            for line in response.iter_lines():
                if line:
                    # Handle both bytes and strings
                    if isinstance(line, bytes):
                        line_str = line.decode('utf-8')
                    else:
                        line_str = line

                    if line_str.startswith('data: '):
                        chunk = line_str[6:]  # Remove 'data: ' prefix
                        chunks.append(chunk)
                        print(chunk, end='', flush=True)

            print()  # New line after streaming
            return chunks

        except Exception as e:
            logger.error(f"Structured generation streaming failed: {e}")
            raise

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()