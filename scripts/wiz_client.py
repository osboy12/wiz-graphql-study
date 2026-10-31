"""Minimal Wiz GraphQL client. Reads config from env / .env (never hard-code secrets)."""
from __future__ import annotations

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_AUTH_URL = "https://auth.app.wiz.io/oauth/token"


class GraphQLError(RuntimeError):
    def __init__(self, errors: list[dict[str, Any]]):
        self.errors = errors
        super().__init__("; ".join(e.get("message", str(e)) for e in errors))


class WizClient:
    def __init__(self) -> None:
        self.client_id = os.environ["WIZ_CLIENT_ID"]
        self.client_secret = os.environ["WIZ_CLIENT_SECRET"]
        self.api_url = os.environ["WIZ_API_URL"]  # https://api.<region>.app.wiz.io/graphql
        self.auth_url = os.environ.get("WIZ_AUTH_URL", DEFAULT_AUTH_URL)
        self.audience = os.environ.get("WIZ_AUDIENCE", "wiz-api")
        self._token: str | None = None
        self._expires_at = 0.0
        self.session = requests.Session()

    def _get_token(self) -> str:
        if self._token and time.time() < self._expires_at - 60:
            return self._token
        resp = self.session.post(
            self.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        self._token = body["access_token"]
        self._expires_at = time.time() + float(body.get("expires_in", 3600))
        return self._token

    def query(self, query: str, variables: dict[str, Any] | None = None, retries: int = 5) -> dict[str, Any]:
        """POST a GraphQL query; returns `data`. Retries on 429/5xx with backoff."""
        delay = 1.0
        for attempt in range(retries):
            resp = self.session.post(
                self.api_url,
                json={"query": query, "variables": variables or {}},
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=120,
            )
            if resp.status_code == 401 and attempt == 0:
                self._token = None  # token may have expired; refresh once
                continue
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(float(resp.headers.get("Retry-After", delay)))
                delay *= 2
                continue
            resp.raise_for_status()
            body = resp.json()
            if body.get("errors"):
                raise GraphQLError(body["errors"])
            return body["data"]
        raise RuntimeError(f"Gave up after {retries} attempts (last status {resp.status_code})")

    def paginate(self, query: str, variables: dict[str, Any], field: str):
        """Yield nodes from connection `field`, following pageInfo.endCursor via $after."""
        variables = dict(variables)
        while True:
            conn = self.query(query, variables)[field]
            yield from conn.get("nodes") or [e["node"] for e in conn.get("edges", [])]
            info = conn["pageInfo"]
            if not info.get("hasNextPage"):
                break
            variables["after"] = info["endCursor"]
