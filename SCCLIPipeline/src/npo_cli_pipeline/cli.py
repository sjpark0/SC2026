from __future__ import annotations

import argparse
import json
import shlex
import sys
import time
import uuid

from celery.result import AsyncResult

from .celery_app import app
from .config import get_settings
from .job_store import create_job, list_jobs, load_job, log_path


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def job_result(job_id: str) -> AsyncResult:
    return AsyncResult(job_id, app=app)


def validate_frame_range(start_frame: int, finish_frame: int) -> None:
    if start_frame > finish_frame:
        raise ValueError("start frame must be less than or equal to finish frame")


def submit_job(operation: str, task_name: str, args: tuple, params: dict) -> int:
    job_id = str(uuid.uuid4())
    create_job(job_id, operation, params)
    app.send_task(task_name, args=(job_id, *args), task_id=job_id)
    print(json.dumps({"job_id": job_id, "status": "queued", "operation": operation}, indent=2))
    return 0


def command_submit(args: argparse.Namespace) -> int:
    if args.submit_command == "preprocess-image":
        params = {
            "source_folder": args.source_folder,
            "target_folder": args.target_folder,
            "factor": args.factor,
        }
        return submit_job(
            "preprocess-image",
            "jobs.preprocess_image",
            (args.source_folder, args.target_folder, args.factor),
            params,
        )

    if args.submit_command == "preprocess-video":
        validate_frame_range(args.start_frame, args.finish_frame)
        params = {
            "source_folder": args.source_folder,
            "target_folder": args.target_folder,
            "factor": args.factor,
            "param_frame": args.param_frame,
            "start_frame": args.start_frame,
            "finish_frame": args.finish_frame,
        }
        return submit_job(
            "preprocess-video",
            "jobs.preprocess_video",
            (
                args.source_folder,
                args.target_folder,
                args.factor,
                args.param_frame,
                args.start_frame,
                args.finish_frame,
            ),
            params,
        )
    if args.submit_command == "init-engine":
        params = {
            "source_folder" : args.source_folder,
            "target_folder" : args.target_folder,
        }
        return submit_job(
            "init-engine",
            "jobs.init_engine",
            (
                args.source_folder,
                args.target_folder,
            ),
            params,
        )
    
    if args.submit_command == "extract-video-frame":
        validate_frame_range(args.start_frame, args.finish_frame)
        params = {
            "source_folder": args.source_folder,
            "target_folder": args.target_folder,            
            "start_frame": args.start_frame,
            "finish_frame": args.finish_frame,
        }
        return submit_job(
            "extract-video-frame",
            "jobs.extract_video_frame",
            (
                args.source_folder,
                args.target_folder,
                args.start_frame,
                args.finish_frame,
            ),
            params,
        )

    if args.submit_command == "build-param":
        params = {
            "source_folder": args.source_folder,
            "target_folder": args.target_folder,            
            "param_frame": args.param_frame,
        }
        return submit_job(
            "build-param",
            "jobs.build_param",
            (
                args.source_folder,
                args.target_folder,
                args.param_frame,
            ),
            params,
        )
    
    if args.submit_command == "build-layer":
        validate_frame_range(args.start_frame, args.finish_frame)
        params = {
            "source_folder": args.source_folder,
            "target_folder": args.target_folder,      
            "factor" : args.factor,      
            "start_frame": args.start_frame,
            "finish_frame": args.finish_frame,
        }
        return submit_job(
            "build-layer",
            "jobs.build_layer",
            (
                args.source_folder,
                args.target_folder,
                args.factor,
                args.start_frame,
                args.finish_frame,
            ),
            params,
        )
    
    if args.submit_command == "render":
        validate_frame_range(args.start_frame, args.finish_frame)
        params = {
            "data_folder": args.data_folder,
            "output_folder": args.output_folder,
            "view_range": args.view_range,
            "focal": args.focal,
            "num_views": args.num_views,
            "start_frame": args.start_frame,
            "finish_frame": args.finish_frame,
        }
        return submit_job(
            "render",
            "jobs.render",
            (
                args.data_folder,
                args.output_folder,
                args.view_range,
                args.focal,
                args.num_views,
                args.start_frame,
                args.finish_frame,
            ),
            params,
        )

    if args.submit_command == "render-quilt-image":
        params = {
            "data_folder": args.data_folder,
            "output_folder": args.output_folder,
            "view_range": args.view_range,
            "focal": args.focal,
            "rows": args.rows,
            "cols": args.cols,
            "frame_number": args.frame_number,
        }
        return submit_job(
            "render-quilt-image",
            "jobs.render_quilt_image",
            (
                args.data_folder,
                args.output_folder,
                args.view_range,
                args.focal,
                args.rows,
                args.cols,
                args.frame_number,
            ),
            params,
        )

    raise ValueError(f"unsupported command: {args.submit_command}")


def command_status(args: argparse.Namespace) -> int:
    job = load_job(args.job_id)
    result = job_result(args.job_id)
    payload = {
        "job": job,
        "celery_state": result.state,
    }
    print(json.dumps(payload, indent=2))
    return 0


def command_list(args: argparse.Namespace) -> int:
    items = list_jobs(limit=args.limit)
    print(json.dumps(items, indent=2))
    return 0


def command_logs(args: argparse.Namespace) -> int:
    path = log_path(args.job_id)
    if not path.exists():
        print(f"log file not found: {path}", file=sys.stderr)
        return 1

    lines = path.read_text(encoding="utf-8").splitlines()
    output = lines[-args.tail:] if args.tail else lines
    for line in output:
        print(line)
    return 0


def command_wait(args: argparse.Namespace) -> int:
    while True:
        job = load_job(args.job_id)
        print(json.dumps({"job_id": args.job_id, "status": job["status"]}, indent=2))
        if job["status"] in {"succeeded", "failed"}:
            return 0 if job["status"] == "succeeded" else 1
        time.sleep(args.interval)


def command_worker(args: argparse.Namespace) -> int:
    argv = [
        "worker",
        "--loglevel",
        args.loglevel,
        "--pool",
        args.pool,
        "--concurrency",
        str(args.concurrency),
    ]
    app.worker_main(argv)
    return 0


def command_shell(_: argparse.Namespace) -> int:
    parser = build_parser()
    print("npo-cli interactive shell")
    print("Type commands like: submit preprocess-image --source-folder ...")
    print("Type 'exit' or 'quit' to leave.")

    while True:
        try:
            raw = input("npo-cli> ").strip()
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue

        if not raw:
            continue

        if raw in {"exit", "quit"}:
            return 0

        try:
            nested_args = parser.parse_args(shlex.split(raw))
            exit_code = nested_args.func(nested_args)
        except SystemExit:
            continue
        except ValueError as error:
            print(str(error), file=sys.stderr)
            continue

        if exit_code:
            print(f"command exited with status {exit_code}", file=sys.stderr)


def command_config(_: argparse.Namespace) -> int:
    settings = get_settings()
    print(
        json.dumps(
            {
                "celery_broker": settings.celery_broker,
                "celery_backend": settings.celery_backend,
                "engine_image": settings.engine_image,
                "host_cwd": settings.host_cwd,
                "state_dir": str(settings.state_dir),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="npo-cli", description="CLI job queue for NPO processing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit_parser = subparsers.add_parser("submit", help="submit a new job")
    submit_subparsers = submit_parser.add_subparsers(dest="submit_command", required=True)

    preprocess_image = submit_subparsers.add_parser("preprocess-image", help="preprocess image dataset")
    preprocess_image.add_argument("--source-folder", required=True)
    preprocess_image.add_argument("--target-folder", required=True)
    preprocess_image.add_argument("--factor", type=positive_int, required=True)
    preprocess_image.set_defaults(func=command_submit)

    preprocess_video = submit_subparsers.add_parser("preprocess-video", help="preprocess video dataset")
    preprocess_video.add_argument("--source-folder", required=True)
    preprocess_video.add_argument("--target-folder", required=True)
    preprocess_video.add_argument("--factor", type=positive_int, required=True)
    preprocess_video.add_argument("--param-frame", type=positive_int, required=True)
    preprocess_video.add_argument("--start-frame", type=non_negative_int, required=True)
    preprocess_video.add_argument("--finish-frame", type=positive_int, required=True)
    preprocess_video.set_defaults(func=command_submit)

    preprocess_video = submit_subparsers.add_parser("init-engine", help="initialize engine")
    preprocess_video.add_argument("--source-folder", required=True)
    preprocess_video.add_argument("--target-folder", required=True)
    preprocess_video.set_defaults(func=command_submit)

    preprocess_video = submit_subparsers.add_parser("extract-video-frame", help="extract video frame")
    preprocess_video.add_argument("--source-folder", required=True)
    preprocess_video.add_argument("--target-folder", required=True)
    preprocess_video.add_argument("--start-frame", type=non_negative_int, required=True)
    preprocess_video.add_argument("--finish-frame", type=positive_int, required=True)
    preprocess_video.set_defaults(func=command_submit)

    preprocess_video = submit_subparsers.add_parser("build-param", help="build param")
    preprocess_video.add_argument("--source-folder", required=True)
    preprocess_video.add_argument("--target-folder", required=True)
    preprocess_video.add_argument("--param-frame", type=positive_int, required=True)
    preprocess_video.set_defaults(func=command_submit)

    preprocess_video = submit_subparsers.add_parser("build-layer", help="build layer")
    preprocess_video.add_argument("--source-folder", required=True)
    preprocess_video.add_argument("--target-folder", required=True)
    preprocess_video.add_argument("--factor", type=positive_int, required=True)
    preprocess_video.add_argument("--start-frame", type=non_negative_int, required=True)
    preprocess_video.add_argument("--finish-frame", type=positive_int, required=True)    
    preprocess_video.set_defaults(func=command_submit)

    render = submit_subparsers.add_parser("render", help="render frame range")
    render.add_argument("--data-folder", required=True)
    render.add_argument("--output-folder", required=True)
    render.add_argument("--view-range", type=float, required=True)
    render.add_argument("--focal", type=positive_int, required=True)
    render.add_argument("--num-views", type=positive_int, required=True)
    render.add_argument("--start-frame", type=positive_int, required=True)
    render.add_argument("--finish-frame", type=positive_int, required=True)
    render.set_defaults(func=command_submit)

    render_quilt = submit_subparsers.add_parser("render-quilt-image", help="render quilt image")
    render_quilt.add_argument("--data-folder", required=True)
    render_quilt.add_argument("--output-folder", required=True)
    render_quilt.add_argument("--view-range", type=float, required=True)
    render_quilt.add_argument("--focal", type=positive_int, required=True)
    render_quilt.add_argument("--rows", type=positive_int, required=True)
    render_quilt.add_argument("--cols", type=positive_int, required=True)
    render_quilt.add_argument("--frame-number", type=positive_int, required=True)
    render_quilt.set_defaults(func=command_submit)

    status = subparsers.add_parser("status", help="show job status")
    status.add_argument("job_id")
    status.set_defaults(func=command_status)

    list_parser = subparsers.add_parser("list", help="list recent jobs")
    list_parser.add_argument("--limit", type=positive_int, default=20)
    list_parser.set_defaults(func=command_list)

    logs = subparsers.add_parser("logs", help="show job logs")
    logs.add_argument("job_id")
    logs.add_argument("--tail", type=positive_int, default=50)
    logs.set_defaults(func=command_logs)

    wait = subparsers.add_parser("wait", help="wait until a job completes")
    wait.add_argument("job_id")
    wait.add_argument("--interval", type=positive_int, default=2)
    wait.set_defaults(func=command_wait)

    worker = subparsers.add_parser("worker", help="start a Celery worker")
    worker.add_argument("--loglevel", default="INFO")
    worker.add_argument("--pool", default="solo")
    worker.add_argument("--concurrency", type=positive_int, default=1)
    worker.set_defaults(func=command_worker)

    shell = subparsers.add_parser("shell", help="open an interactive submit shell")
    shell.set_defaults(func=command_shell)

    config = subparsers.add_parser("config", help="show effective configuration")
    config.set_defaults(func=command_config)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
