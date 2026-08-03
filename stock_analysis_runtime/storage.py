"""Atomic immutable JSON artifact storage and publication verification."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .models import ContractError


def reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON constant: {value}")


def decode_json(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("malformed UTF-8") from exc

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ContractError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(text, object_pairs_hook=pairs, parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ContractError("artifact must be a JSON object")
    return value


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode()


class ArtifactStore:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str, artifact_id: str) -> Path:
        for part in (session_id, artifact_id):
            if not part or part in {".", ".."} or "/" in part or "\\" in part:
                raise ContractError("path traversal rejected")
        path = (self.root / session_id / f"{artifact_id}.json").resolve()
        if self.root not in path.parents:
            raise ContractError("path traversal rejected")
        return path

    def put(self, session_id: str, artifact_id: str, value: dict[str, Any]) -> dict[str, Any]:
        target = self._path(session_id, artifact_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            existing = target.read_bytes()
            raw = canonical_bytes(value)
            if existing == raw:
                return self.receipt(target, raw, replay=True)
            raise ContractError("generation collision or immutable artifact modification")
        raw = canonical_bytes(value)
        fd, temp_name = tempfile.mkstemp(dir=target.parent, prefix=".pending-")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        readback = target.read_bytes()
        if readback != raw:
            raise ContractError("readback verification failed")
        return self.receipt(target, raw, replay=False)

    @staticmethod
    def receipt(path: Path, raw: bytes, replay: bool) -> dict[str, Any]:
        value = decode_json(raw)
        return {
            "accepted": True,
            "integrity_verified": True,
            "identical_replay": replay,
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "canonical_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
            "byte_length": len(raw),
            "artifact": path.name,
        }

    def verify(self, session_id: str) -> dict[str, Any]:
        directory = (self.root / session_id).resolve()
        if not directory.is_dir():
            raise ContractError("unknown session")
        inventory = []
        for path in sorted(directory.iterdir()):
            if path.is_symlink() or not path.is_file() or path.suffix != ".json":
                raise ContractError("unexpected file or symlink")
            raw = path.read_bytes()
            decode_json(raw)
            inventory.append(self.receipt(path, raw, replay=False))
        return {"integrity_verified": True, "inventory": inventory}
