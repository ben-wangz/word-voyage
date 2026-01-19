# OpenAI Client Pool
from typing import Tuple
from threading import Lock
from openai import OpenAI


class ClientPool:
    """
    Thread-safe OpenAI client pool
    Reuses clients with same (base_url, api_key) configuration
    """

    def __init__(self):
        self._clients: dict[Tuple[str, str], OpenAI] = {}
        self._lock = Lock()

    def get_client(self, base_url: str, api_key: str) -> OpenAI:
        """
        Get or create OpenAI client for given configuration

        Args:
            base_url: OpenAI API base URL
            api_key: OpenAI API key

        Returns:
            OpenAI client instance
        """
        key = (base_url, api_key)

        with self._lock:
            if key not in self._clients:
                self._clients[key] = OpenAI(base_url=base_url, api_key=api_key)
            return self._clients[key]


# Singleton instance
client_pool = ClientPool()
