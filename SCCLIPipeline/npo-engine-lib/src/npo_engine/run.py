import os
import docker
import docker.errors

from loguru import logger
from pathlib import Path

from . import exceptions as ex
#from typing import Callable
#LogFn = Callable[[str], None]

host_cwd = os.environ.get("HOST_CWD")
logger.info(f"HOST_CWD : {host_cwd}")


def get_path_for_host(folder: str) -> Path:
    # 컨테이너 내부일 경우(host_cwd 값이 있을 경우), 해당 경로 이후로
    # 아닐 경우, 절대 경로
    if host_cwd:
        return Path(host_cwd) / folder
    else:
        return Path(folder).absolute()


def bind_mount(source: Path, target: str, read_only: bool = False) -> docker.types.Mount:
    return docker.types.Mount(
        target=target,
        source=str(source),
        type="bind",
        read_only=read_only,
    )


def init(image: str, data_folder: str, input_folder: str, output_folder: str):
    input_path = get_path_for_host(input_folder)
    data_path = get_path_for_host(data_folder)
    output_path = get_path_for_host(output_folder)

    logger.info("init()")
    logger.info(f'input  : {input_path}')
    logger.info(f'data   : {data_path}')
    logger.info(f'output : {output_path}')

    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(input_path, "/etri_workspace/Input", read_only=True),
            bind_mount(output_path, "/etri_workspace/Output"),
            bind_mount(data_path, "/etri_workspace/Data"),
        ]
        command = "python run_init.py"

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command
        
    except Exception as err:
        raise ex.EngineException(f"{err}", err)


def extract_frames(image: str, data_folder: str, output_folder: str, start_frame: int, finish_frame: int):
    data_path = get_path_for_host(data_folder)
    output_path = get_path_for_host(output_folder)

    logger.info("extract_frames()")
    logger.info(f'data         : {data_path}')
    logger.info(f'output       : {output_path}')
    logger.info(f'start_frame  : {start_frame}')
    logger.info(f'finish_frame : {finish_frame}')
    
    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(output_path, "/etri_workspace/Output"),
            bind_mount(data_path, "/etri_workspace/Data"),
        ]
        command = f'python run_extract_frames.py ' \
            f'--start_frame {start_frame} ' \
            f'--end_frame {finish_frame}'

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command
    except Exception as err:
        raise ex.EngineException(f"{err}", err)


def build_param(image: str, data_folder: str, frame_number: int):
    data_path = get_path_for_host(data_folder)

    logger.info("build_param()")
    logger.info(f'data   : {data_path}')

    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(data_path.absolute(), "/etri_workspace/Data"),
        ]
        command = f'python run_build_param.py ' \
            f'--frame_number {frame_number}'

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command
    except Exception as err:
        raise ex.EngineException(f"{err}", err)


def build_layer(image: str, data_folder: str, factor: float, frame_number: int):
    data_path = get_path_for_host(data_folder)

    logger.info("build_layer()")
    logger.info(f'data   : {data_path}')

    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(data_path.absolute(), "/etri_workspace/Data"),
        ]
        command = f'python run_build_layer.py ' \
            f'--factor {factor} ' \
            f'--frame_number {frame_number}'

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command
    except Exception as err:
        raise ex.EngineException(f"{err}", err)


def render(image: str,
           data_folder: str, output_folder: str,
           view_range: float, focal: int, num_views: int, frame_number: int,
           save_viewing: bool):
    data_path = get_path_for_host(data_folder)
    output_path = get_path_for_host(output_folder)

    logger.info("render()")
    logger.info(f'data   : {data_path}')
    logger.info(f'output : {output_path}')

    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(data_path, "/etri_workspace/Data"),
            bind_mount(output_path, "/etri_workspace/Output"),
        ]
        command = f'python run_render.py ' \
            f'--view_range {view_range} ' \
            f'--focal {focal} ' \
            f'--num_views {num_views} ' \
            f'--frame_number {frame_number}'
        if save_viewing:
            command += " --save_viewing"

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command

    except Exception as err:
        raise ex.EngineException(f"{err}", err)


def render_quilt_image(image: str,
                       data_folder: str, output_folder: str,
                       view_range: float, focal: int,
                       rows: int, cols: int, frame_number: int):
    data_path = get_path_for_host(data_folder)
    output_path = get_path_for_host(output_folder)

    logger.info("render_quilt_image()")
    logger.info(f'data   : {data_path}')
    logger.info(f'output : {output_path}')

    try:
        client = docker.from_env()
        devices = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]  # `--gpus all`과 동일
        mounts = [
            bind_mount(data_path, "/etri_workspace/Data"),
            bind_mount(output_path, "/etri_workspace/Output"),
        ]
        command = f'python run_render_quilt.py ' \
            f'--view_range {view_range} ' \
            f'--focal {focal} ' \
            f'--rows {rows} ' \
            f'--cols {cols} ' \
            f'--frame_number {frame_number} '

        return client.containers.run(image=image,
                                     command=command,
                                     mounts=mounts,
                                     device_requests=devices,  # GPU 설정
                                     #  remove=True,
                                     detach=True), command

    except Exception as err:
        raise ex.EngineException(f"{err}", err)
