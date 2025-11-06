# src/gh_client.py
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv


class GitHubError(Exception):
    pass


class GitHubClient:
    """
    Minimal GitHub REST API client using httpx.
    Reads token from env var GITHUB_TOKEN (loaded from .env if present).
    """

    base_url = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, timeout: float = 15.0):
        load_dotenv()
        token = token or os.getenv("GITHUB_TOKEN")

        headers = {"accept": "application/vnd.github+json",
                   "user-agent": "gh-client/0.1"}
        if token:
            headers["authorization"] = f"Bearer {token}"

        self.client = httpx.Client(base_url=self.base_url,
                                   headers=headers,
                                   timeout=timeout)

    # ---- low-level helpers ----
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None):
        r = self.client.get(path, params=params)
        # rate limit special-case
        if r.status_code == 403 and r.headers.get("x-ratelimit-remaining") == "0":
            reset = r.headers.get("x-ratelimit-reset")
            raise GitHubError(f"Rate limit exceeded. Reset at epoch {reset}. Add a token or wait.")
        if r.is_error:
            # try to surface GH message
            try:
                msg = r.json().get("message", r.text)
            except Exception:
                msg = r.text
            raise GitHubError(f"{r.status_code} Error: {msg}")
        # success
        if "application/json" in r.headers.get("content-type", ""):
            return r.json()
        return r.text

    # ---- public methods ----
    def get_authenticated_user(self) -> Dict[str, Any]:
        return self._get("/user")

    def get_user(self, username: str) -> Dict[str, Any]:
        return self._get(f"/users/{username}")

    def list_user_repos(self, username: str, per_page: int = 30, sort: str = "updated") -> List[Dict[str, Any]]:
        return self._get(f"/users/{username}/repos",
                         params={"per_page": per_page, "sort": sort})

    def list_repo_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        return self._get(f"/repos/{owner}/{repo}/issues", params={"state": state})
