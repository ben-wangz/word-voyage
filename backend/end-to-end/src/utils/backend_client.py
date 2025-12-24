"""WordVoyage Backend Game Client"""

import httpx
from typing import Dict, Any, List


class BackendGameClient:
    """Client for WordVoyage Backend game service"""

    def __init__(self, service_url: str, timeout: int = 60):
        """Initialize client

        Args:
            service_url: Backend service URL
            timeout: Request timeout in seconds (default 60s)
        """
        self.service_url = service_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        self.service_name = None

        # Get service info
        try:
            health = self.health_check()
            self.service_name = health.get("status", "unknown")
        except Exception:
            self.service_name = "unknown"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close HTTP client"""
        if self.client:
            self.client.close()

    def health_check(self) -> Dict[str, Any]:
        """Check service health

        Returns:
            Health check response
        """
        response = self.client.get(f"{self.service_url}/api/health")
        response.raise_for_status()
        return response.json()

    def start_game(self) -> Dict[str, Any]:
        """Start a new game

        Returns:
            Response with initial step and sessionId
        """
        response = self.client.post(f"{self.service_url}/api/game/start")
        response.raise_for_status()
        return response.json()

    def process_step(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process user input step

        Args:
            session_id: Game session ID
            user_input: User input text

        Returns:
            Response with new step and sessionId
        """
        payload = {
            "sessionId": session_id,
            "input": user_input
        }
        response = self.client.post(
            f"{self.service_url}/api/game/step",
            json=payload
        )

        # Print error details if request failed
        if response.status_code not in [200, 201]:
            try:
                error_detail = response.json()
                print(f"Error response: {error_detail}")
            except:
                print(f"Error response text: {response.text}")

        response.raise_for_status()
        return response.json()

    def process_step_raw(
        self,
        payload: Dict[str, Any]
    ) -> httpx.Response:
        """Process step with raw payload (for validation testing)

        Args:
            payload: Request payload

        Returns:
            Raw HTTP response
        """
        return self.client.post(
            f"{self.service_url}/api/game/step",
            json=payload
        )

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get current game context

        Args:
            session_id: Game session ID

        Returns:
            Current context
        """
        response = self.client.get(f"{self.service_url}/api/game/context/{session_id}")
        response.raise_for_status()
        return response.json()

    def get_history(self, session_id: str) -> Dict[str, Any]:
        """Get game step history

        Args:
            session_id: Game session ID

        Returns:
            Response with steps array
        """
        response = self.client.get(f"{self.service_url}/api/game/history/{session_id}")
        response.raise_for_status()
        return response.json()
