import sys
import argparse
from loguru import logger
from pathlib import Path
import subprocess
import common
import version as V

def build_layer(factor: int, frame_number: int):
    logger.info(f"action_build_layer()")
    scene_dir = Path(common.SCENE_DIR)

    subprocess.run(['make_layer', scene_dir / 'Param', scene_dir / 'Image' / str(frame_number), scene_dir / 'Layer' / str(frame_number), str(factor)], check=True)
    #raise Exception("Data file is not exist.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"ETRI Spatial Computing Engine v{V.VERSION}")
    parser.add_argument('--factor', type=str, required=True, help='Specify factor.')
    parser.add_argument('--frame_number', type=int, default=1, help='Specify frame number.')

    args = parser.parse_args()
    try:
        build_layer(args.factor, args.frame_number)

        logger.info("Success")
        sys.exit(0)

    except Exception as ex:
        # 에러 발생시 로그 출력하고, exit_code를 0이 아닌 값으로 설정
        logger.error(ex)
        sys.exit(1)
