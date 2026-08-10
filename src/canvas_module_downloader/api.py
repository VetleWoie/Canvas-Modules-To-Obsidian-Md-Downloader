from urllib.parse import urljoin

import requests


class AuthError(RuntimeError):
    pass


class CanvasClient:
    def __init__(self, base_url: str, token: str | None = None, cookie: str | None = None):
        if not token and not cookie:
            raise ValueError("CanvasClient requires either a token or a cookie")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        if cookie:
            self.session.headers["Cookie"] = cookie
        self.session.headers["User-Agent"] = "canvas-module-downloader"

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        response = self.session.get(url, params=params)
        if response.status_code in (401, 403):
            raise AuthError(
                "Canvas rejected the request (401/403). Your token or session cookie may be "
                "invalid, expired, or lack access to this course."
            )
        response.raise_for_status()
        return response

    @staticmethod
    def _as_json(response: requests.Response):
        try:
            return response.json()
        except ValueError as e:
            raise AuthError(
                "Canvas didn't return JSON (likely redirected to a login page). "
                "If you're using a session cookie, it has probably expired - log into "
                "Canvas again and grab a fresh one."
            ) from e

    def _get_paginated(self, path: str, params: dict | None = None) -> list[dict]:
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        results = []
        while url:
            response = self._get(url, params=params)
            results.extend(self._as_json(response))
            url = response.links.get("next", {}).get("url")
            params = None
        return results

    def get_json(self, url_or_path: str) -> dict:
        url = urljoin(self.base_url + "/", url_or_path.lstrip("/"))
        return self._as_json(self._get(url))

    def get_course(self, course_id: str) -> dict:
        return self.get_json(f"/api/v1/courses/{course_id}")

    def list_modules(self, course_id: str) -> list[dict]:
        return self._get_paginated(
            f"/api/v1/courses/{course_id}/modules", params={"per_page": 100}
        )

    def list_module_items(self, course_id: str, module_id: int) -> list[dict]:
        return self._get_paginated(
            f"/api/v1/courses/{course_id}/modules/{module_id}/items",
            params={"per_page": 100},
        )
