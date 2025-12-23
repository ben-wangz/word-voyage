"""LLM Service client for tests"""

import httpx
from typing import Dict, Any, Optional


class LLMClient:
    """Client for LLM Service API"""

    def __init__(self, service_url: str, timeout: int = 30):
        """Initialize client

        Args:
            service_url: Base URL of LLM service
            timeout: Request timeout in seconds
        """
        self.service_url = service_url.rstrip('/')
        self.timeout = timeout
        self._client = None
        self.service_name = None

    def __enter__(self):
        """Context manager entry"""
        self._client = httpx.Client(timeout=self.timeout)
        
        # Get service info from health endpoint
        try:
            response = self._client.get(f"{self.service_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.service_name = health_data.get("service", "unknown")
        except Exception:
            pass
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._client:
            self._client.close()

    def health_check(self) -> Dict[str, Any]:
        """Check service health

        Returns:
            Health status data
        """
        response = self._client.get(f"{self.service_url}/health")
        response.raise_for_status()
        return response.json()

    def generate_structured(
        self,
        prompt: str,
        context: Dict[str, Any],
        schema: Dict[str, Any],
        pre_log_summary: Optional[Dict[str, Any]] = None,
        user_input: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured data

        Args:
            prompt: Generation prompt
            context: Game context
            schema: Output schema definition
            pre_log_summary: Historical events summary
            user_input: User's current input
            model: Model override

        Returns:
            Generation response
        """
        request_data = {
            "prompt": prompt,
            "context": context,
            "schema": schema,
            "stream": False
        }

        if pre_log_summary:
            request_data["pre_log_summary"] = pre_log_summary

        if user_input:
            request_data["user_input"] = user_input

        if model:
            request_data["model"] = model

        response = self._client.post(
            f"{self.service_url}/generate_structured",
            json=request_data
        )
        response.raise_for_status()
        return response.json()
