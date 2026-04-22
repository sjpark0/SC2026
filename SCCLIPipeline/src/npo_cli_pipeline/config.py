from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _default_state_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "state"


@dataclass(frozen=True)
class Settings:
    celery_broker: str
    celery_backend: str
    engine_image: str
    host_cwd: str | None
    state_dir: Path


def get_settings() -> Settings:
    raw_state_dir = os.getenv("NPO_CLI_STATE_DIR", "").strip()
    state_dir = Path(raw_state_dir).expanduser() if raw_state_dir else _default_state_dir()

    return Settings(
        celery_broker=os.getenv("CELERY_BROKER", "redis://localhost:20108/0"),
        celery_backend=os.getenv("CELERY_BACKEND", "redis://localhost:20108/1"),
        engine_image=os.getenv("ENGINE_IMAGE", "devboxhq/npo:etri_scapi-0.1.4"),
        host_cwd=os.getenv("HOST_CWD") or None,
        state_dir=state_dir.resolve(),
    )
