import requests
from src.utils.logger import logger


class BaseAPI:
    def __init__(self, agent_token: str = None) -> None:
        self.agent_token = agent_token

    def _get_header(self, auth_req=True, extra_headers=None, has_body=False):
        """Generate request headers dynamically based on auth requirement and extra headers."""
        if not auth_req and not extra_headers and not has_body:
            return None  # No headers required

        header = {}

        if auth_req and self.agent_token:
            header["Authorization"] = f"Bearer {self.agent_token}"

        if has_body:
            header["Content-Type"] = "application/json"  # Only add if body is present

        if extra_headers:
            header.update(extra_headers)

        return header

    def _get_request(self, url, auth_req=True, extra_headers=None, params=None):
        """Helper method to handle GET requests with error handling."""
        try:
            headers = self._get_header(auth_req, extra_headers, has_body=False)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
            return None

    def _post_request(
        self, url, data=None, auth_req=True, extra_headers=None, params=None
    ):
        """Helper method to handle POST requests with error handling."""
        try:
            headers = self._get_header(
                auth_req, extra_headers, has_body=(data is not None)
            )

            response = requests.post(url, json=data, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            return None

    def _patch_request(
        self, url, data=None, auth_req=True, extra_headers=None, params=None
    ):
        """Helper method to handle PATCH requests with error handling."""
        try:
            headers = self._get_header(
                auth_req, extra_headers, has_body=(data is not None)
            )
            response = requests.patch(url, json=data, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"PATCH request failed: {e}")
            return None
