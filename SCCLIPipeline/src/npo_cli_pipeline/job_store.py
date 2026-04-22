from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_dir() -> Path:
    return get_settings().state_dir


def jobs_dir() -> Path:
    path = _state_dir() / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = _state_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def job_path(job_id: str) -> Path:
    return jobs_dir() / f"{job_id}.json"


def log_path(job_id: str) -> Path:
    return logs_dir() / f"{job_id}.log"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    temp_path.replace(path)


def create_job(job_id: str, operation: str, params: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "job_id": job_id,
        "operation": operation,
        "status": "queued",
        "params": params,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "result": None,
        "error": None,
    }
    _write_json(job_path(job_id), payload)
    return payload


def load_job(job_id: str) -> dict[str, Any]:
    path = job_path(job_id)
    if not path.exists():
        raise FileNotFoundError(f"job not found: {job_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_job(payload: dict[str, Any]) -> dict[str, Any]:
    payload["updated_at"] = utc_now()
    _write_json(job_path(payload["job_id"]), payload)
    return payload


def update_job(job_id: str, **changes: Any) -> dict[str, Any]:
    payload = load_job(job_id)
    payload.update(changes)
    return save_job(payload)


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(jobs_dir().glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
        if len(items) >= limit:
            break
    return items
