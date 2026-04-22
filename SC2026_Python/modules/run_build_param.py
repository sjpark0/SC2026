import sys
import argparse
from loguru import logger
from pathlib import Path
import subprocess

import common
import version as V


def build_param(frame_number : int):
    # 컨테이너 내부에 항상 고정된 위치에 폴더 위치
    # pathlib.Path를 사용하시면, 윈도우/리눅스에서 경로 처리가 간단합니다.
    
    #logger.info(f"PARAM_DIR: {common.PARAM_DIR} {Path(common.PARAM_DIR).absolute()}")
    #logger.info(f"IMAGE_DIR: {common.IMAGE_DIR} {Path(common.IMAGE_DIR).absolute()}")
    #logger.info(f"LAYER_DIR: {common.LAYER_DIR} {Path(common.LAYER_DIR).absolute()}")
    scene_dir = Path(common.SCENE_DIR)
    (scene_dir / 'Param' / 'sparse').mkdir(parents=True, exist_ok=True)

    
    subprocess.run(['colmap', 'feature_extractor', '--database_path', scene_dir / 'Param' / 'database.db', '--image_path', scene_dir / 'Image' / str(frame_number) / 'images'], check=True)
    subprocess.run(['colmap', 'exhaustive_matcher', '--database_path', scene_dir / 'Param' / 'database.db'], check=True)
    subprocess.run(['colmap', 'mapper','--database_path', scene_dir / 'Param' / 'database.db', '--image_path', scene_dir / 'Image' / str(frame_number) / 'images', '--output_path', scene_dir / 'Param' / 'sparse'], check=True)            
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"ETRI Spatial Computing Engine v{V.VERSION}")   
    parser.add_argument('--frame_number', type=int, default=1, help='Specify frame number.')

    args = parser.parse_args()
    
    try:
        build_param(args.frame_number)
    
        logger.info("Success")
        sys.exit(0)

    except Exception as ex:
        # 에러 발생시 로그 출력하고, exit_code를 0이 아닌 값으로 설정
        logger.error(ex)
        sys.exit(1)
