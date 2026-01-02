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
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)
        self.service_name = None
        self._session_id = None

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

    def start_game(self, lang: str = None) -> Dict[str, Any]:
        """Start a new game

        Args:
            lang: Optional language code (en, zh)

        Returns:
            Response with initial step and sessionId
        """
        url = f"{self.service_url}/api/game/start"
        params = {"lang": lang} if lang else None
        response = self.client.post(url, params=params)
        response.raise_for_status()
        result = response.json()
        self._session_id = result.get("sessionId")
        return result

    def get_session_id(self) -> str:
        """Get current session ID from cookie

        Returns:
            Current session ID
        """
        return self._session_id

    def process_step(self, user_input: str) -> Dict[str, Any]:
        """Process user input step

        Args:
            user_input: User input text

        Returns:
            Response with new step and sessionId
        """
        payload = {"input": user_input}
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

    def get_context(self, lang: str = None) -> Dict[str, Any]:
        """Get current game context

        Args:
            lang: Optional language code (en, zh)

        Returns:
            Current context
        """
        url = f"{self.service_url}/api/game/context/{self._session_id}"
        params = {"lang": lang} if lang else None
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_history(self) -> Dict[str, Any]:
        """Get game step history

        Returns:
            Response with steps array
        """
        response = self.client.get(f"{self.service_url}/api/game/history/{self._session_id}")
        response.raise_for_status()
        return response.json()

    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """Register anonymous user with email/password

        Args:
            email: User email
            password: User password

        Returns:
            Response with userId, email, accessToken, refreshToken
        """
        response = self.client.post(
            f"{self.service_url}/api/auth/register",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login with email/password

        Args:
            email: User email
            password: User password

        Returns:
            Response with userId, email, accessToken, refreshToken
        """
        response = self.client.post(
            f"{self.service_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def logout(self, refresh_token: str) -> Dict[str, Any]:
        """Logout and revoke refresh token

        Args:
            refresh_token: Refresh token to revoke

        Returns:
            Response with success message
        """
        response = self.client.post(
            f"{self.service_url}/api/auth/logout",
            json={"refreshToken": refresh_token}
        )
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token

        Args:
            refresh_token: Refresh token

        Returns:
            Response with new accessToken and refreshToken
        """
        response = self.client.post(
            f"{self.service_url}/api/auth/refresh",
            json={"refreshToken": refresh_token}
        )
        response.raise_for_status()
        return response.json()

    def set_jwt_header(self, access_token: str):
        """Set JWT Authorization header

        Args:
            access_token: JWT access token
        """
        self.client.headers["Authorization"] = f"Bearer {access_token}"

    def clear_jwt_header(self):
        """Clear JWT Authorization header"""
        self.client.headers.pop("Authorization", None)

    def get_context_by_id(self, session_id: str, lang: str = None) -> httpx.Response:
        """Get context by session ID (raw response for testing)

        Args:
            session_id: Session ID
            lang: Optional language code

        Returns:
            Raw HTTP response
        """
        url = f"{self.service_url}/api/game/context/{session_id}"
        params = {"lang": lang} if lang else None
        return self.client.get(url, params=params)

    def get_history_by_id(self, session_id: str) -> httpx.Response:
        """Get history by session ID (raw response for testing)

        Args:
            session_id: Session ID

        Returns:
            Raw HTTP response
        """
        return self.client.get(f"{self.service_url}/api/game/history/{session_id}")
