from loguru import logger

from enum import StrEnum
from pathlib import Path

from . import exceptions as ex

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}


class Modality(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


def check_modality(folder: str) -> Modality:
    logger.info("check_modality()")
    logger.info(f'folder : {folder}')

    path = Path(folder)
    if not path.exists() or not path.is_dir():
        raise ex.EngineException(f"Folder is not exist : {folder}")

    for file in path.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            if ext in IMAGE_EXTS:
                return Modality.IMAGE
            elif ext in VIDEO_EXTS:
                return Modality.VIDEO

    raise ex.EngineException(f'No image or video files found in the folder. : {folder}')
