from __future__ import annotations

import json
import os
from typing import Any

import httpx


class OpenAICompatibleBackend:
    """Optional structured-output backend for local or hosted OpenAI-compatible APIs."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("LLM_BASE_URL", "")
        self.api_key = os.environ.get("LLM_API_KEY", "")
        self.model = os.environ.get("LLM_MODEL", "")

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.model)

    def complete_json(self, messages: list[dict[str, str]], schema: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("LLM backend is not configured")
        response = httpx.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            json={"model": self.model, "messages": messages, "response_format": {"type": "json_schema", "json_schema": {"name": "diagnosis", "schema": schema}}},
            timeout=60,
        )
        response.raise_for_status()
        return json.loads(response.json()["choices"][0]["message"]["content"])
