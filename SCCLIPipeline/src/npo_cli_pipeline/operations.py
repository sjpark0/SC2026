from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Callable

from npo_engine import run as engine_run

from .config import get_settings

LogFn = Callable[[str], None]


def _ensure_directory(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _ensure_existing_directory(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"{label} is not a directory: {resolved}")
    return resolved


def _copy_source_if_needed(source_folder: str, target_folder: str, log: LogFn) -> Path:
    source = _ensure_existing_directory(source_folder, "source folder")
    target = Path(target_folder).expanduser().resolve()

    if source == target:
        target.mkdir(parents=True, exist_ok=True)
        log(f"Using source folder in place: {target}")
        return target

    target.mkdir(parents=True, exist_ok=True)
    log(f"Copying source data from {source} to {target}")
    shutil.copytree(source, target, dirs_exist_ok=True)
    return target


def _prepare_video_workspace(source_folder: str, target_folder: str, log: LogFn) -> Path:
    source = _ensure_existing_directory(source_folder, "source folder")
    target = _ensure_directory(target_folder)
    video_dir = target / "Video"
    video_dir.mkdir(parents=True, exist_ok=True)

    if source == target:
        if not video_dir.exists():
            raise FileNotFoundError(f"missing video workspace: {video_dir}")
        log(f"Using existing video workspace: {target}")
        return target

    log(f"Preparing video workspace from {source} to {video_dir}")
    shutil.copytree(source, video_dir, dirs_exist_ok=True)
    return target


def _wait_for_file(path: Path, log: LogFn, timeout_seconds: float = 5.0, interval_seconds: float = 0.2) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(interval_seconds)
    log(f"Timed out waiting for file to appear: {path}")
    return path.exists()


def _resolve_extracted_frames(work_folder: Path, param_frame: int, log: LogFn) -> tuple[int, int, int]:
    log(work_folder)
    result_json = work_folder / "extract_frames_result.json"
    log("_resolve_extracted_frames")

    if _wait_for_file(result_json, log):
        log("_resolve_extracted_frames")
        data = json.loads(result_json.read_text(encoding="utf-8"))
        actual_start = int(data["start_frame"])
        actual_finish = int(data["end_frame"])
        actual_param = min(max(param_frame, actual_start), actual_finish)
        log(
            "Frame range resolved from extract_frames_result.json to "
            f"start={actual_start}, finish={actual_finish}, param_frame={actual_param}"
        )
        return actual_start, actual_finish, actual_param

    raise FileNotFoundError(f"missing frame extraction result: {result_json}")


def _run_container(container, command: str, log: LogFn, remove: bool = True) -> None:
    log(f"Command: {command}")
    try:
        for line in container.logs(stream=True):
            msg = line.decode("utf-8", errors="replace").rstrip()
            if msg:
                log(msg)

        result = container.wait()
        exit_code = result.get("StatusCode")
        if exit_code != 0:
            raise RuntimeError(f"non-zero exit status: {exit_code}")
    finally:
        if remove:
            container.remove()


def preprocess_image(job_id: str, source_folder: str, target_folder: str, factor: int, log: LogFn) -> dict:
    settings = get_settings()
    work_folder = _copy_source_if_needed(source_folder, target_folder, log)

    container, command = engine_run.build_param(settings.engine_image, str(work_folder), 1)
    _run_container(container, command, log)

    container, command = engine_run.build_layer(settings.engine_image, str(work_folder), factor, 1)
    _run_container(container, command, log)

    return {
        "job_id": job_id,
        "work_folder": str(work_folder),
        "factor": factor,
    }


def preprocess_video(
    job_id: str,
    source_folder: str,
    target_folder: str,
    factor: int,
    param_frame: int,
    start_frame: int,
    finish_frame: int,
    log: LogFn,
) -> dict:
    settings = get_settings()
    work_folder = _prepare_video_workspace(source_folder, target_folder, log)

    log(f"Extracting frames from {work_folder} to {work_folder}")
    container, command = engine_run.extract_frames(
        settings.engine_image,
        str(work_folder),
        str(work_folder),
        start_frame,
        finish_frame,
    )
    _run_container(container, command, log, remove=False)
    try:
        actual_start, actual_finish, actual_param = _resolve_extracted_frames(work_folder, param_frame, log)
    finally:
        container.remove()

    container, command = engine_run.build_param(settings.engine_image, str(work_folder), actual_param)
    _run_container(container, command, log)

    total = actual_finish - actual_start + 1
    for index, frame in enumerate(range(actual_start, actual_finish + 1), start=1):
        log(f"Building layer {index}/{total} for frame {frame}")
        container, command = engine_run.build_layer(settings.engine_image, str(work_folder), factor, frame)
        _run_container(container, command, log)

    return {
        "job_id": job_id,
        "work_folder": str(work_folder),
        "factor": factor,
        "start_frame": actual_start,
        "finish_frame": actual_finish,
        "param_frame": actual_param,
    }
def init_engine(
    job_id : str,
    source_folder: str,
    target_folder: str,
    log: LogFn,
) -> dict:
    settings = get_settings()
    source = _ensure_existing_directory(source_folder, "source folder")
    target = _ensure_directory(target_folder)
    
    log(f"init engine from {source} to {target}")
    container, command = engine_run.init(
        settings.engine_image,
        str(target),
        str(source),
        str(target),
    )
    _run_container(container, command, log)
    return {
        "job_id": job_id,
        "work_folder": str(target),
    }

def extract_video_frame(
    job_id : str,
    source_folder: str,
    target_folder: str,
    start_frame: int,
    finish_frame: int,
    log: LogFn,
) -> dict:
    settings = get_settings()
    #work_folder = _prepare_video_workspace(source_folder, target_folder, log)
    
    work_folder = _ensure_directory(target_folder)
    log(f"Extracting frames from {work_folder} to {work_folder}")
    container, command = engine_run.extract_frames(
        settings.engine_image,
        str(work_folder),
        str(work_folder),
        start_frame,
        finish_frame,
    )
    _run_container(container, command, log)
    return {
        "job_id": job_id,
        "work_folder": str(work_folder),
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }

def build_param(
    job_id : str,
    source_folder: str,
    target_folder: str,
    param_frame: int,    
    log: LogFn,
) -> dict:
    settings = get_settings()
    #work_folder = _prepare_video_workspace(source_folder, target_folder, log)
    work_folder = _ensure_directory(target_folder)
    actual_start, actual_finish, actual_param = _resolve_extracted_frames(work_folder, param_frame, log)
    
    container, command = engine_run.build_param(settings.engine_image, str(work_folder), actual_param)
    _run_container(container, command, log)
    return {
        "job_id": job_id,
        "work_folder": str(work_folder),
        "start_frame": actual_start,
        "finish_frame": actual_finish,
        "param_frame": actual_param,
    }

def build_layer(
    job_id : str,
    source_folder: str,
    target_folder: str,
    factor: int,
    start_frame: int,
    finish_frame: int,
    log: LogFn,
) -> dict:
    settings = get_settings()
    #work_folder = _prepare_video_workspace(source_folder, target_folder, log)
    work_folder = _ensure_directory(target_folder)
    result_json = work_folder / "extract_frames_result.json"
    if _wait_for_file(result_json, log):
        data = json.loads(result_json.read_text(encoding="utf-8"))
        actual_start = max(start_frame, int(data["start_frame"]))
        actual_finish = min(finish_frame, int(data["end_frame"]))

    total = actual_finish - actual_start + 1
    for index, frame in enumerate(range(actual_start, actual_finish + 1), start=1):
        log(f"Building layer {index}/{total} for frame {frame}")
        container, command = engine_run.build_layer(settings.engine_image, str(work_folder), factor, frame)
        _run_container(container, command, log)

    return {
        "job_id": job_id,
        "work_folder": str(work_folder),
        "factor": factor,
        "start_frame": actual_start,
        "finish_frame": actual_finish,
    }

def render(
    job_id: str,
    data_folder: str,
    output_folder: str,
    view_range: float,
    focal: int,
    num_views: int,
    start_frame: int,
    finish_frame: int,
    log: LogFn,
) -> dict:
    settings = get_settings()
    data = _ensure_existing_directory(data_folder, "data folder")
    output = _ensure_directory(output_folder)

    total = finish_frame - start_frame + 1
    for index, frame in enumerate(range(start_frame, finish_frame + 1), start=1):
        log(f"Rendering frame {frame} ({index}/{total})")
        frame_output = output / str(frame)
        frame_output.mkdir(parents=True, exist_ok=True)
        container, command = engine_run.render(
            settings.engine_image,
            str(data),
            str(frame_output),
            view_range,
            focal,
            num_views,
            frame,
            frame == start_frame,
        )
        _run_container(container, command, log)

    return {
        "job_id": job_id,
        "data_folder": str(data),
        "output_folder": str(output),
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }


def render_quilt_image(
    job_id: str,
    data_folder: str,
    output_folder: str,
    view_range: float,
    focal: int,
    rows: int,
    cols: int,
    frame_number: int,
    log: LogFn,
) -> dict:
    settings = get_settings()
    data = _ensure_existing_directory(data_folder, "data folder")
    output = _ensure_directory(output_folder)

    container, command = engine_run.render_quilt_image(
        settings.engine_image,
        str(data),
        str(output),
        view_range,
        focal,
        rows,
        cols,
        frame_number,
    )
    _run_container(container, command, log)

    return {
        "job_id": job_id,
        "data_folder": str(data),
        "output_folder": str(output),
        "rows": rows,
        "cols": cols,
        "frame_number": frame_number,
    }
