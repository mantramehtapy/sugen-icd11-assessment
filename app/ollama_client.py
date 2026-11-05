from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from typing import Any

from .schemas import parse_model_codes


class OllamaClient:
    def __init__(
        self,
        post: Callable[[str, dict[str, Any], float], dict[str, Any]] | None = None,
        model: str = "gemma4:e4b",
        endpoint: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.post = post or self._post
        self.model = model
        host = endpoint or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        host = host.rstrip("/")
        self.endpoint = host if host.endswith("/api/chat") else f"{host}/api/chat"
        self.timeout = timeout
        self.stats = {
            "calls": 0,
            "successes": 0,
            "parse_failures": 0,
            "timeouts": 0,
            "transport_failures": 0,
        }

    def choose(self, candidates: list[dict[str, str]], note: str) -> list[str]:
        prompt = {
            "note": note,
            "candidates": candidates,
            "instruction": "Choose only from candidates. Return JSON only with a codes array.",
        }
        payload = {
            "model": self.model,
            "stream": False,
            "format": {"type": "object", "properties": {"codes": {"type": "array"}}, "required": ["codes"]},
            "messages": [
                {"role": "system", "content": "You are a careful ICD-11 adjudicator."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
        }
        try:
            self.stats["calls"] += 1
            response = self.post(self.endpoint, payload, self.timeout)
            content = response.get("message", {}).get("content", "")
            codes = parse_model_codes(content)
            if not codes:
                self.stats["parse_failures"] += 1
                return []
            self.stats["successes"] += 1
            return codes
        except TimeoutError:
            self.stats["timeouts"] += 1
            return []
        except (OSError, TypeError, ValueError, KeyError):
            self.stats["transport_failures"] += 1
            return []

    @staticmethod
    def _post(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
