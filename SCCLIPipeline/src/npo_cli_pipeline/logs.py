from __future__ import annotations

from datetime import datetime, timezone

from .job_store import log_path


def append_log(job_id: str, message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    path = log_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")
