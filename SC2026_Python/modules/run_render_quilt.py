import sys
import argparse
from loguru import logger
from pathlib import Path

import common
import version as V
import SCAPI
import cv2

def render_quilt(view_range: float, focal: float, rows: int, cols: int, frame_number : int):
    logger.info(f"action_build_param()")
    logger.info(f"view_range : {view_range}")
    logger.info(f"focal      : {focal}")
    logger.info(f"rows       : {rows}")
    logger.info(f"cols       : {cols}")
    logger.info(f"frame_number : {frame_number}")
    # 컨테이너 내부에 항상 고정된 위치에 폴더 위치
    # pathlib.Path를 사용하시면, 윈도우/리눅스에서 경로 처리가 간단합니다.
    
    # SCAPI 호출등 엔진 기능 구현
    scene_dir = Path(common.SCENE_DIR)

    api = SCAPI.SCAPI()
    m = api.SetInputFolder(scene_dir / 'Param', scene_dir / 'Layer' / str(frame_number))
    q = api.MakeQuiltImage(view_range, focal, rows, cols)
    cv2.imwrite(Path(common.OUTPUT_DIR) / "res_qs{:d}x{:d}.png".format(rows, cols), q)
    api.Finalize()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"ETRI Spatial Computing Engine v{V.VERSION}")
    parser.add_argument('--view_range', type=float, required=True, help='Specify view_range.')
    parser.add_argument('--focal', type=float, required=True, help='Specify focal.')
    parser.add_argument('--rows', type=int, required=True, help='Specify rows.')
    parser.add_argument('--cols', type=int, required=True, help='Specify cols.')
    parser.add_argument('--frame_number', type=int, default=1, help='Specify frame number.')
    args = parser.parse_args()

    try:
        render_quilt(**vars(args))

        logger.info("Success")
        sys.exit(0)

    except Exception as ex:
        # 에러 발생시 로그 출력하고, exit_code를 0이 아닌 값으로 설정
        logger.error(ex)
        sys.exit(1)
