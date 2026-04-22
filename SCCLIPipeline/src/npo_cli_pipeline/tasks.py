from __future__ import annotations

import time

from celery.app.task import Task

from .celery_app import app
from .job_store import update_job
from .logs import append_log
from . import operations


def _job_logger(job_id: str):
    return lambda message: append_log(job_id, message)


def _retry_update_job(job_id: str, **changes) -> None:
    last_error: Exception | None = None
    for _ in range(10):
        try:
            update_job(job_id, **changes)
            return
        except FileNotFoundError as error:
            last_error = error
            time.sleep(0.2)
    if last_error is not None:
        raise last_error


def _start_job(job_id: str, payload: dict) -> None:
    _retry_update_job(job_id, status="running")
    append_log(job_id, f"Job started: {payload}")


def _finish_job(job_id: str, result: dict) -> dict:
    _retry_update_job(job_id, status="succeeded", result=result, error=None)
    append_log(job_id, "Job finished successfully")
    return result


def _fail_job(job_id: str, error: Exception) -> None:
    _retry_update_job(job_id, status="failed", error=str(error))
    append_log(job_id, f"Job failed: {error}")


@app.task(bind=True, name="jobs.preprocess_image")
def preprocess_image_task(
    self: Task,
    job_id: str,
    source_folder: str,
    target_folder: str,
    factor: int,
) -> dict:
    payload = {
        "operation": "preprocess-image",
        "source_folder": source_folder,
        "target_folder": target_folder,
        "factor": factor,
    }
    _start_job(job_id, payload)
    try:
        result = operations.preprocess_image(job_id, source_folder, target_folder, factor, _job_logger(job_id))
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise


@app.task(bind=True, name="jobs.preprocess_video")
def preprocess_video_task(
    self: Task,
    job_id: str,
    source_folder: str,
    target_folder: str,
    factor: int,
    param_frame: int,
    start_frame: int,
    finish_frame: int,
) -> dict:
    payload = {
        "operation": "preprocess-video",
        "source_folder": source_folder,
        "target_folder": target_folder,
        "factor": factor,
        "param_frame": param_frame,
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }
    _start_job(job_id, payload)
    try:
        result = operations.preprocess_video(
            job_id,
            source_folder,
            target_folder,
            factor,
            param_frame,
            start_frame,
            finish_frame,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise


@app.task(bind=True, name="jobs.extract_video_frame")
def extract_video_frame_task(
    self: Task,
    job_id: str,
    source_folder: str,
    target_folder: str,
    start_frame: int,
    finish_frame: int,
) -> dict:
    payload = {
        "operation": "extract-video-frame",
        "source_folder": source_folder,
        "target_folder": target_folder,
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }
    _start_job(job_id, payload)
    try:
        result = operations.extract_video_frame(
            job_id,
            source_folder,
            target_folder,
            start_frame,
            finish_frame,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise


@app.task(bind=True, name="jobs.build_param")
def build_param_task(
    self: Task,
    job_id: str,
    source_folder: str,
    target_folder: str,
    param_frame: int,
) -> dict:
    payload = {
        "operation": "build-param",
        "source_folder": source_folder,
        "target_folder": target_folder,
        "param_frame": param_frame,
    }
    _start_job(job_id, payload)
    try:
        result = operations.build_param(
            job_id,
            source_folder,
            target_folder,
            param_frame,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise

@app.task(bind=True, name="jobs.build_layer")
def build_layer_task(
    self: Task,
    job_id: str,
    source_folder: str,
    target_folder: str,
    factor: int,
    start_frame: int,
    finish_frame: int,
) -> dict:
    payload = {
        "operation": "build-layer",
        "source_folder": source_folder,
        "target_folder": target_folder,
        "factor": factor,
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }
    _start_job(job_id, payload)
    try:
        result = operations.build_layer(
            job_id,
            source_folder,
            target_folder,
            factor,
            start_frame, 
            finish_frame,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise

@app.task(bind=True, name="jobs.render")
def render_task(
    self: Task,
    job_id: str,
    data_folder: str,
    output_folder: str,
    view_range: float,
    focal: int,
    num_views: int,
    start_frame: int,
    finish_frame: int,
) -> dict:
    payload = {
        "operation": "render",
        "data_folder": data_folder,
        "output_folder": output_folder,
        "view_range": view_range,
        "focal": focal,
        "num_views": num_views,
        "start_frame": start_frame,
        "finish_frame": finish_frame,
    }
    _start_job(job_id, payload)
    try:
        result = operations.render(
            job_id,
            data_folder,
            output_folder,
            view_range,
            focal,
            num_views,
            start_frame,
            finish_frame,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise


@app.task(bind=True, name="jobs.render_quilt_image")
def render_quilt_image_task(
    self: Task,
    job_id: str,
    data_folder: str,
    output_folder: str,
    view_range: float,
    focal: int,
    rows: int,
    cols: int,
    frame_number: int,
) -> dict:
    payload = {
        "operation": "render-quilt-image",
        "data_folder": data_folder,
        "output_folder": output_folder,
        "view_range": view_range,
        "focal": focal,
        "rows": rows,
        "cols": cols,
        "frame_number": frame_number,
    }
    _start_job(job_id, payload)
    try:
        result = operations.render_quilt_image(
            job_id,
            data_folder,
            output_folder,
            view_range,
            focal,
            rows,
            cols,
            frame_number,
            _job_logger(job_id),
        )
        return _finish_job(job_id, result)
    except Exception as error:
        _fail_job(job_id, error)
        raise
