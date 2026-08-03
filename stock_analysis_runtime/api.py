"""Bearer-authenticated stdlib WSGI REST API for a private deployment."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable, Iterable
from typing import Any
from wsgiref.simple_server import make_server

from .models import ContractError
from .state import SessionRuntime


class App:
    def __init__(self, storage: str, token: str):
        self.runtime, self.token = SessionRuntime(storage), token

    def __call__(self, env: dict[str, Any], start: Callable[..., Any]) -> Iterable[bytes]:
        try:
            path, method = env["PATH_INFO"], env["REQUEST_METHOD"]
            if path == "/health":
                return self._reply(start, 200, {"status": "ok", "llm": False})
            if env.get("HTTP_AUTHORIZATION") != f"Bearer {self.token}":
                return self._reply(start, 401, {"error": "unauthorized"})
            length = int(env.get("CONTENT_LENGTH") or 0)
            body = json.loads(env["wsgi.input"].read(length) or b"{}")
            parts = path.strip("/").split("/")
            if method == "POST" and path == "/v1/sessions":
                result = self.runtime.create(body)
            elif len(parts) >= 3 and parts[:2] == ["v1", "sessions"]:
                sid = parts[2]
                if method == "GET" and parts[3:] == ["next"]:
                    result = self.runtime.next_contract(sid)
                elif method == "POST" and parts[3:] == ["artifacts"]:
                    result = self.runtime.submit(sid, body["kind"], body["phase"], body["artifact"])
                elif method == "POST" and parts[3:] == ["reconciliation", "disclose"]:
                    result = self.runtime.disclose(sid, body)
                elif method == "POST" and parts[3:] == ["updates"]:
                    result = self.runtime.start_update(
                        sid, body["update_id"], body["source_cutoff"]
                    )
                elif method == "GET" and parts[3:] == ["integrity"]:
                    result = self.runtime.publication(sid)
                elif method == "GET" and parts[3:] in (["handoff"], ["ledger"]):
                    result = self.runtime.final_component(sid, parts[3])
                else:
                    return self._reply(start, 404, {"error": "not found"})
            else:
                return self._reply(start, 404, {"error": "not found"})
            return self._reply(start, 200, result)
        except (ContractError, KeyError, ValueError, json.JSONDecodeError) as exc:
            return self._reply(start, 400, {"error": str(exc)})

    @staticmethod
    def _reply(start: Callable[..., Any], status: int, value: Any) -> list[bytes]:
        raw = json.dumps(value).encode()
        start(
            f"{status} {'OK' if status == 200 else 'Error'}",
            [("Content-Type", "application/json"), ("Content-Length", str(len(raw)))],
        )
        return [raw]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--storage", default=os.getenv("STOCK_ANALYSIS_STORAGE", "/data"))
    args = parser.parse_args()
    token = os.getenv("STOCK_ANALYSIS_TOKEN")
    if not token:
        raise SystemExit("STOCK_ANALYSIS_TOKEN is required")
    with make_server(args.host, args.port, App(args.storage, token)) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
